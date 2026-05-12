from django.db import models
from apps.scraper.models import ScrapeJob  

# Create your models here.
class Subject(models.Model):
    subject_code = models.CharField(primary_key=True, max_length=10)
    subject_name = models.CharField(max_length=255)
    semester = models.IntegerField()
    subject_credits = models.IntegerField(null=True, blank=True)

class StudentResult(models.Model):
    job = models.ForeignKey(ScrapeJob, on_delete=models.PROTECT)
    usn = models.CharField(max_length=10)
    student_name = models.CharField(max_length=255)

    class Meta:
        unique_together = [('job', 'usn')]

class SubjectMark(models.Model):
    class ResultChoices(models.TextChoices):
        PASS = 'P', 'Pass'
        FAIL = 'F', 'Fail'
        ABSENT = 'A', 'Absent'
        WITHHELD = 'W', 'Withheld'
        NOT_ELIGIBLE = 'NE', 'Not Eligible'

    student_result = models.ForeignKey(StudentResult, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.IntegerField()
    is_backlog = models.BooleanField(default=False)
    internal_marks = models.IntegerField(null=True, blank=True)
    external_marks = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=2, choices=ResultChoices.choices)
    announced_on = models.DateField(null=True, blank=True)

    # Reval fields (null if not reval)
    old_result = models.CharField(max_length=2, choices=ResultChoices.choices, blank=True)
    reval_marks = models.IntegerField(null=True, blank=True)
    reval_result = models.CharField(max_length=2, choices=ResultChoices.choices, blank=True)

    class Meta:
        unique_together = [('student_result', 'subject', 'semester')]

class AnalysisReport(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        RUNNING   = 'running',   'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED    = 'failed',    'Failed'

    job = models.OneToOneField(ScrapeJob, on_delete=models.PROTECT)
    excel_file  = models.FileField(upload_to='reports/excel/',  null=True, blank=True)
    chart_image = models.ImageField(upload_to='reports/charts/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

class SubjectStats(models.Model):
    report = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    appeared = models.IntegerField()
    passed = models.IntegerField()
    failed = models.IntegerField()
    absent = models.IntegerField()
    withheld = models.IntegerField()
    not_eligible = models.IntegerField()
    pass_percentage = models.DecimalField(max_digits=5, decimal_places=2)

class StudentSGPA(models.Model):
    report = models.ForeignKey(AnalysisReport, on_delete=models.PROTECT)
    student_result = models.ForeignKey(StudentResult, on_delete=models.CASCADE)
    sgpa = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        unique_together = [('report', 'student_result')]
