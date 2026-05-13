import re
from rest_framework import serializers
from apps.scraper.models import ScrapeJob
from apps.analyzer.models import AnalysisReport


class ScrapeJobCreateSerializer(serializers.ModelSerializer):
    usn_prefix = serializers.CharField()
    usn_sequence = serializers.CharField()

    class Meta:
        model  = ScrapeJob
        fields = [
            'usn_prefix', 'usn_sequence', 'exam_semester',
            'result_url', 'retry_delay', 'retry_count'
        ]

    def validate_usn_prefix(self, value):
        value = value.upper().strip()
        if not re.match(r'^\d[A-Z]{2}\d{2}[A-Z]{2}$', value):
            raise serializers.ValidationError('Invalid USN prefix format.')
        return value

    def validate_exam_semester(self, value):
        if value not in range(1, 9):
            raise serializers.ValidationError('Semester must be between 1 and 8.')
        return value

    def validate_result_url(self, value):
        if not re.match(r'^https://results\.vtu\.ac\.in/[a-zA-Z0-9]+/index\.php$', value):
            raise serializers.ValidationError('Invalid VTU result URL.')
        return value

    def validate_usn_sequence(self, value):
        try:
            result = self._parse_sequence(value.strip())
        except (ValueError, AttributeError):
            raise serializers.ValidationError('Invalid format. Use ranges (1-100), comma lists (1,2,3), or both (1,2-5).')
        if not result:
            raise serializers.ValidationError('Sequence cannot be empty.')
        return result

    def _parse_sequence(self, s: str) -> list:
        def parse_part(part: str) -> list:
            part = part.strip()
            if '-' in part:
                pieces = part.split('-')
                if len(pieces) != 2:
                    raise ValueError(f'Invalid range: {part!r}')
                start, end = int(pieces[0]), int(pieces[1])
                if start > end:
                    start, end = end, start
                return list(range(start, end + 1))
            return [int(part)]

        seq = []
        for part in s.split(','):
            seq.extend(parse_part(part))
        return sorted(set(seq))

    def validate(self, data):
        data['is_reval'] = 'RV' in data['result_url'].upper()
        return data

class ScrapeJobStatusSerializer(serializers.ModelSerializer):
    analysis_status = serializers.SerializerMethodField()

    class Meta:
        model  = ScrapeJob
        fields = ['id', 'usn_prefix', 'usn_sequence',
            'exam_semester', 'status', 'progress',
            'error_log', 'analysis_status',
        ]
        read_only_fields = fields

    def get_analysis_status(self, obj):
        try:
            report = AnalysisReport.objects.get(job_id=obj.id)
            return report.status
        except AnalysisReport.DoesNotExist:
            return None