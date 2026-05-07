from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.analyzer.models import AnalysisReport
from .serializers import AnalyzeRequestSerializer
from apps.analyzer.tasks import analyze_task

class AnalyzeJobView(APIView):
    def post(self, request):
        serializer = AnalyzeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = serializer.validated_data['job_id']
        analyze_task.delay(job_id)
        return Response({'message': 'Analysis started'}, status=status.HTTP_202_ACCEPTED)

class AnalysisResultView(APIView):
    def get(self, request, job_id):
        try:
            report = AnalysisReport.objects.get(job_id=job_id)
        except AnalysisReport.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'status': 'completed'}, status=status.HTTP_200_OK)