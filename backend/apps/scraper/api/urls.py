from django.urls import path
from .views import ScrapeJobCreateView, ScrapeJobStatusView

urlpatterns = [
    path('jobs/', ScrapeJobCreateView.as_view()),
    path('jobs/<int:pk>/status/', ScrapeJobStatusView.as_view()),
]
