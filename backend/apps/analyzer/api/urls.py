from django.urls import path
from .views import AnalyzeJobView, AnalysisResultView

urlpatterns = [
    path('analyze/', AnalyzeJobView.as_view()),
    path('results/<int:job_id>/', AnalysisResultView.as_view()),
]
