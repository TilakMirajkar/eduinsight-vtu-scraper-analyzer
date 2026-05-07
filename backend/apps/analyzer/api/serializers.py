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