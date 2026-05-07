from rest_framework import serializers
from apps.analyzer import models

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model  = models.Subject
        fields = '__all__'

class StudentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model  = models.StudentResult
        fields = ['id', 'usn', 'student_name']

class AnalyzeRequestSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()

    def validate_job_id(self, value):
        from apps.scraper.models import ScrapeJob
        try:
            job = ScrapeJob.objects.get(id=value)
        except ScrapeJob.DoesNotExist:
            raise serializers.ValidationError('Job not found.')
        if job.status != ScrapeJob.Status.COMPLETED:
            raise serializers.ValidationError('Job is not completed yet.')
        return value