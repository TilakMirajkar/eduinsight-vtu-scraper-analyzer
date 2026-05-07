from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.analyzer.models import AnalysisReport
from .serializers import AnalyzeRequestSerializer
from apps.analyzer.tasks import analyze_task
from django.http import FileResponse
import os

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
        return Response({
            'job_id': report.job_id,
            'created_at': report.created_at,
            'excel_file': report.excel_file.url if report.excel_file else None,
            'chart_image': report.chart_image.url if report.chart_image else None,
        }, status=status.HTTP_200_OK)

class DownloadExcelView(APIView):
    def get(self, request, job_id):
        try:
            report = AnalysisReport.objects.get(job_id=job_id)
        except AnalysisReport.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        if not report.excel_file:
            return Response({'error': 'Excel file not generated'}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            report.excel_file.open('rb'),
            as_attachment=True,
            filename=os.path.basename(report.excel_file.name)
        )

class DownloadChartView(APIView):
    def get(self, request, job_id):
        try:
            report = AnalysisReport.objects.get(job_id=job_id)
        except AnalysisReport.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        if not report.chart_image:
            return Response({'error': 'Chart not generated'}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            report.chart_image.open('rb'),
            as_attachment=True,
            filename=os.path.basename(report.chart_image.name)
        )