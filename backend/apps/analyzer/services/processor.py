from apps.analyzer.models import StudentResult, SubjectMark, Subject, AnalysisReport

RESULT_MAP = {
    'P': 'P',
    'P *': 'P',
    'F': 'F',
    'A': 'A',
    'W': 'W',
    'X': 'NE',
    'NE': 'NE',
}

def _clean_text(text: str) -> str:
    return text.strip()

def normalize_result(raw: str) -> str:
    return RESULT_MAP.get(raw.strip().upper(), 'NE')

def _parse_int(value: str):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def _parse_date(value: str):
    from datetime import datetime
    try:
        return datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

def save_scraped_results(job, soup_dict: dict) -> None:
    is_reval = job.is_reval

    for student_key, soup in soup_dict.items():
        usn, student_name = student_key.split('+', 1)

        student_result, _ = StudentResult.objects.update_or_create(
            job=job,
            usn=usn,
            defaults={'student_name': student_name}
        )

        # Each div with this style = one semester block header
        sems_divs = soup.find_all('div', style='text-align:center;padding:5px;')
        sems_num = [x.text.split(':')[-1].strip() for x in sems_divs]
        sems_data = [sem_div.find_next_sibling('div') for sem_div in sems_divs]

        marks_to_create = []

        for sem, marks_data in zip(sems_num, sems_data):
            if not marks_data:
                continue

            rows = marks_data.find_all('div', class_='divTableRow')
            if len(rows) < 2:
                continue

            # First row = headers, rest = data
            data = []
            for row in rows:
                cells = row.find_all('div', class_='divTableCell')
                data.append([_clean_text(cell.text) for cell in cells])

            headers = data[0]    # ['Subject Code', 'Subject Name', 'Internal Marks', ...]
            body_rows = data[1:]

            for row in body_rows:
                if len(row) < 2:
                    continue

                subject_code = _clean_text(row[0])
                subject_name = _clean_text(row[1])

                # Map remaining columns to values
                # Regular: exclude last column (Announced date is last)
                # Reval:   include all columns
                if not is_reval:
                    mark_headers = headers[2:-1]
                    mark_values = row[2:-1]
                    announced = _parse_date(row[-1]) if row[-1] else None
                else:
                    mark_headers = headers[2:]
                    mark_values = row[2:]
                    announced = None

                payload = dict(zip(mark_headers, mark_values))

                subject, _ = Subject.objects.get_or_create(
                    subject_code=subject_code,
                    defaults={
                        'subject_name': subject_name,
                        'semester': int(sem),
                    }
                )

                marks_to_create.append(
                    SubjectMark(
                        student_result=student_result,
                        subject=subject,
                        semester=int(sem),
                        is_backlog=int(sem) != job.exam_semester,
                        internal_marks=_parse_int(payload.get('Internal Marks')),
                        external_marks=_parse_int(payload.get('External Marks')),
                        total=_parse_int(payload.get('Total')),
                        result=normalize_result(payload.get('Result', '')),
                        announced_on=announced,
                        # Reval fields
                        old_result=normalize_result(payload.get('Old Result', '')) if is_reval else '',
                        reval_marks=_parse_int(payload.get('Final Marks')) if is_reval else None,
                        reval_result=normalize_result(payload.get('Final Result', '')) if is_reval else '',
                    )
                )

        if marks_to_create:
            SubjectMark.objects.bulk_create(marks_to_create)


def analyze_and_save(job) -> AnalysisReport:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.core.files.base import ContentFile
    from collections import defaultdict
    from apps.analyzer.models import (
        StudentResult, SubjectMark, Subject,
        AnalysisReport, SubjectStats, StudentSGPA
    )

    students = StudentResult.objects.filter(
        job=job
    ).prefetch_related('subjectmark_set__subject')

    # --- Per-subject stat accumulators ---
    subject_stats = defaultdict(lambda: {
        'appeared': 0, 'passed': 0, 'failed': 0,
        'absent': 0, 'withheld': 0, 'not_eligible': 0
    })

    # --- Create report first so FKs work ---
    report, _ = AnalysisReport.objects.get_or_create(job=job)

    # --- SGPA + subject stats loop ---
    for student in students:
        regular_marks = student.subjectmark_set.filter(
            semester=job.exam_semester
        )

        # Accumulate subject stats
        for mark in regular_marks:
            code = mark.subject.subject_code
            result = mark.result

            if result != 'A':
                subject_stats[code]['appeared'] += 1
            if result == 'P':
                subject_stats[code]['passed'] += 1
            elif result == 'F':
                subject_stats[code]['failed'] += 1
            elif result == 'A':
                subject_stats[code]['absent'] += 1
            elif result == 'W':
                subject_stats[code]['withheld'] += 1
            elif result == 'NE':
                subject_stats[code]['not_eligible'] += 1

        # SGPA — only if all subjects have credits
        all_marks = student.subjectmark_set.filter(
            semester=job.exam_semester
        ).select_related('subject')

        credits_available = all(
            m.subject.subject_credits is not None
            for m in all_marks
        )

        if credits_available and all_marks.exists():
            num, den = 0, 0
            for mark in all_marks:
                c = mark.subject.subject_credits
                gp = _to_grade_point(mark.total, mark.result)
                num += gp * c
                den += c

            sgpa = round(num / den, 2) if den > 0 else 0.0

            StudentSGPA.objects.update_or_create(
                report=report,
                student_result=student,
                defaults={'sgpa': sgpa}
            )

    # --- Save SubjectStats ---
    subjects = Subject.objects.filter(
        subject_code__in=subject_stats.keys()
    )
    subject_map = {s.subject_code: s for s in subjects}

    stats_to_create = []
    labels, pass_percentages = [], []

    for code, stats in subject_stats.items():
        appeared = stats['appeared']
        passed   = stats['passed']
        pct      = round(passed / appeared * 100, 2) if appeared > 0 else 0.0

        stats_to_create.append(
            SubjectStats(
                report       = report,
                subject      = subject_map[code],
                appeared     = appeared,
                passed       = passed,
                failed       = stats['failed'],
                absent       = stats['absent'],
                withheld     = stats['withheld'],
                not_eligible = stats['not_eligible'],
                pass_percentage = pct,
            )
        )
        labels.append(code)
        pass_percentages.append(pct)

    SubjectStats.objects.filter(report=report).delete()
    SubjectStats.objects.bulk_create(stats_to_create)

    # --- Generate chart ---
    fig, ax = plt.subplots(figsize=(max(10, len(labels) * 1.5), 6))
    ax.bar(labels, pass_percentages)
    ax.set_xlabel('Subject Code')
    ax.set_ylabel('Pass Percentage')
    ax.set_title('Subject-wise Pass Percentages')
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')

    for i, pct in enumerate(pass_percentages):
        ax.text(i, pct + 1, f'{pct}%', ha='center', fontsize=8)

    fig.tight_layout()

    # Save chart to report
    buf = io.BytesIO()
    fig.savefig(buf, format='jpg')
    buf.seek(0)
    report.chart_image.save(
        f'chart_job_{job.id}.jpg',
        ContentFile(buf.read()),
        save=False
    )
    plt.close(fig)

    generate_excel(job, report)
    report.save()
    return report


def _to_grade_point(total, result: str) -> int:
    if result != 'P' or total is None:
        return 0
    if total >= 90: return 10
    if total >= 80: return 9
    if total >= 70: return 8
    if total >= 60: return 7
    if total >= 55: return 6
    if total >= 50: return 5
    if total >= 40: return 4
    return 0

def generate_excel(job, report) -> None:
    import io
    import pandas as pd
    from django.core.files.base import ContentFile
    from apps.analyzer.models import (
        StudentResult, SubjectMark,
        SubjectStats, StudentSGPA
    )

    # --- Student-wise results ---
    marks_qs = SubjectMark.objects.filter(
        student_result__job=job
    ).select_related('student_result', 'subject')

    student_rows = []
    for m in marks_qs:
        student_rows.append({
            'USN': m.student_result.usn,
            'Student Name': m.student_result.student_name,
            'Subject Code': m.subject.subject_code,
            'Subject Name': m.subject.subject_name,
            'Semester': m.semester,
            'Is Backlog': m.is_backlog,
            'Internal Marks': m.internal_marks,
            'External Marks': m.external_marks,
            'Total': m.total,
            'Result': m.result,
            'Announced On': m.announced_on,
        })
    student_df = pd.DataFrame(student_rows)

    # --- Subject-wise stats ---
    stats_qs = SubjectStats.objects.filter(
        report=report
    ).select_related('subject')

    stats_rows = []
    for s in stats_qs:
        stats_rows.append({
            'Subject Code': s.subject.subject_code,
            'Subject Name': s.subject.subject_name,
            'Appeared': s.appeared,
            'Passed': s.passed,
            'Failed': s.failed,
            'Absent': s.absent,
            'Withheld': s.withheld,
            'Not Eligible': s.not_eligible,
            'Pass Percentage': s.pass_percentage,
        })
    stats_df = pd.DataFrame(stats_rows)

    # --- SGPA ---
    sgpa_qs = StudentSGPA.objects.filter(
        report=report
    ).select_related('student_result')

    sgpa_rows = []
    for s in sgpa_qs:
        sgpa_rows.append({
            'USN':          s.student_result.usn,
            'Student Name': s.student_result.student_name,
            'SGPA':         s.sgpa,
        })
    sgpa_df = pd.DataFrame(sgpa_rows)

    # --- Write Excel ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        student_df.to_excel(writer, sheet_name='Student-wise Results', index=False)
        stats_df.to_excel(writer, sheet_name='Subject-wise Stats', index=False)
        if not sgpa_df.empty:
            sgpa_df.to_excel(writer, sheet_name='SGPA Report', index=False)

    output.seek(0)
    excel_name = f'analysis_job_{job.id}.xlsx'
    report.excel_file.save(
        excel_name,
        ContentFile(output.read()),
        save=False
    )
