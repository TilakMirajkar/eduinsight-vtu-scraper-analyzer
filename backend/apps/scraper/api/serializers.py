import re
from rest_framework import serializers
from apps.scraper.models import ScrapeJob


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
        if not re.match(r'^\d{1,3}([-,]\d{1,3})*$', value.strip()):
            raise serializers.ValidationError('Enter numbers in format: 1-100 or 1,2,3 or 1,2-5')
        return self._parse_sequence(value)

    def _parse_sequence(self, s: str) -> list:
        def parse_part(part):
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start > end:
                    start, end = end, start
                return list(range(start, end + 1))
            return [int(part)]

        seq = []
        for part in s.split(','):
            seq.extend(parse_part(part.strip()))
        return sorted(set(seq))

    def validate(self, data):
        data['is_reval'] = 'RV' in data['result_url'].upper()
        return data

class ScrapeJobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ScrapeJob
        fields = [
            'id', 'status', 'progress',
            'error_log', 'created_at', 'completed_at'
        ]
        read_only_fields = fields