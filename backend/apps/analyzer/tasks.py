from celery import shared_task
from apps.scraper.models import ScrapeJob
from apps.analyzer.models import AnalysisReport
from apps.analyzer.services.processor import analyze_and_save

@shared_task(soft_time_limit=1800, time_limit=1860)
def analyze_task(job_id):
    try:
        job = ScrapeJob.objects.get(id=job_id)
    except ScrapeJob.DoesNotExist:
        return

    try:
        analyze_and_save(job)
    except Exception as e:
        AnalysisReport.objects.filter(job=job).update(status=AnalysisReport.Status.FAILED)
        raise