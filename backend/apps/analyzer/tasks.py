from celery import shared_task
from apps.scraper.models import ScrapeJob
from apps.analyzer.services.processor import analyze_and_save

@shared_task
def analyze_task(job_id):
    try:
        job = ScrapeJob.objects.get(id=job_id)
        analyze_and_save(job)
    except Exception as e:
        raise