from django.contrib import admin
from .models import Subject, StudentResult, SubjectMark, AnalysisReport, SubjectStats, StudentSGPA

admin.site.register(Subject)
admin.site.register(StudentResult)
admin.site.register(SubjectMark)
admin.site.register(AnalysisReport)
admin.site.register(SubjectStats)
admin.site.register(StudentSGPA)