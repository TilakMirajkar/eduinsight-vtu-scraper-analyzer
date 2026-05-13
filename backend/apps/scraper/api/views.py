from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from apps.scraper.models import ScrapeJob
from .serializers import ScrapeJobCreateSerializer, ScrapeJobStatusSerializer
from apps.scraper.tasks import scrape_task

class ScrapeJobListCreateView(ListCreateAPIView):
    queryset = ScrapeJob.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ScrapeJobCreateSerializer
        return ScrapeJobStatusSerializer

    def perform_create(self, serializer):
        self.job = serializer.save()
        scrape_task.delay(self.job.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'id': self.job.id, 'status': self.job.status},  # job's id and status
            status=status.HTTP_201_CREATED
        )

class ScrapeJobStatusView(RetrieveAPIView):
    serializer_class = ScrapeJobStatusSerializer
    queryset = ScrapeJob.objects.all()