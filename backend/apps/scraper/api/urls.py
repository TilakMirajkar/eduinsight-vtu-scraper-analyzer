from django.urls import path
from .views import ScrapeJobListCreateView, ScrapeJobStatusView

urlpatterns = [
    path('jobs/', ScrapeJobListCreateView.as_view()),
    path('jobs/<int:pk>/status/', ScrapeJobStatusView.as_view()),
]
