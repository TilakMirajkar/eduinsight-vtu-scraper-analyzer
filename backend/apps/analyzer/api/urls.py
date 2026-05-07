from django.urls import path
from .views import AnalyzeJobView, AnalysisResultView, DownloadExcelView, DownloadChartView

urlpatterns = [
    path('analyze/', AnalyzeJobView.as_view()),
    path('results/<int:job_id>/', AnalysisResultView.as_view()),
    path('results/<int:job_id>/download/excel/', DownloadExcelView.as_view()),
    path('results/<int:job_id>/download/chart/', DownloadChartView.as_view()),
]
