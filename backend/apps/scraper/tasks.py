from celery import shared_task
from django.utils import timezone
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from apps.scraper.models import ScrapeJob, SkippedUSN
from apps.scraper.services.scraper import Connection
from apps.analyzer.services.processor import save_scraped_results

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task(soft_time_limit=3600, time_limit=3660)
def scrape_task(job_id):
    try:
        job = ScrapeJob.objects.get(id=job_id)
    except ScrapeJob.DoesNotExist:
        logger.error(f"ScrapeJob {job_id} not found.")
        return

    conn = Connection()
    soup_dict = {}
    total = len(job.usn_sequence)
    abort = False
    cool_counter = 0

    try:
        job.status = ScrapeJob.Status.RUNNING
        job.save(update_fields=['status'])

        conn.connect(job.result_url, mode=False)

        for i, num in enumerate(job.usn_sequence):
            usn = f'{job.usn_prefix}{num:03d}'
            logger.info(f"Processing USN: {usn}")
            this_retry = 0

            while this_retry < job.retry_count:
                try:
                    conn.enter_usn(usn)

                    captcha_text, error = conn.get_captcha()
                    if error:
                        job.error_log += 'Error! Tesseract not configured. Retry after configuring.\n'
                        abort = True
                        break

                    elif len(captcha_text) != 6:
                        job.error_log += 'Invalid captcha. Trying again.\n'
                        conn.driver.refresh()
                        continue
                    
                    else:
                        conn.captcha_submit(captcha_text)
                        conn.sleep(1)

                    soup_dict = conn.get_info(soup_dict)
                    job.error_log += f'Data collected for {usn}\n'
                    cool_counter = 0
                    
                    break 

                except UnexpectedAlertPresentException:
                    try:
                        alert = conn.check_alert()
                        alert_text = alert.text
                    except TimeoutException:
                        this_retry += 1
                        conn.driver.refresh()
                        continue

                    job.error_log += f'Error for {usn}: {alert_text}\n'

                    if alert_text in ['University Seat Number is not available or Invalid..!', 
                                      'You have not applied for reval or reval results are awaited !!!']:
                        cool_counter += 1
                        job.error_log += f'Moving to the next USN.\n'
                        SkippedUSN.objects.create(job=job, usn=usn, reason=alert_text)
                        alert.accept()
                        break

                    elif alert_text == '':
                        job.error_log += f'\nUnfortunately, this IP address has been blocked...\n'
                        abort = True
                        alert.accept()
                        break

                    else:
                        cool_counter += 1
                        job.error_log += 'Trying again.\n'
                        this_retry += 1
                        alert.accept()

                except Exception:
                    occur = conn.stuck_page()
                    if occur:
                        conn.driver.back()
                        this_retry += 1
                    else:
                        this_retry += 1
                        conn.sleep(job.retry_delay)
                        conn.driver.refresh()

            else:
                job.error_log += f'Max retries exhausted for {usn}. Skipping.\n'
                SkippedUSN.objects.create(job=job, usn=usn, reason='Max retries exhausted')

            job.progress = int((i + 1) / total * 100)
            job.save(update_fields=['error_log', 'progress'])

            if cool_counter > 5:
                job.error_log += 'Waiting to avoid IP block.\n'
                job.save(update_fields=['error_log'])
                conn.sleep(3)
                cool_counter = 0

            if abort:
                break

            conn.driver.get(job.result_url)

        if soup_dict:
            save_scraped_results(job, soup_dict)

        if abort:
            job.status = ScrapeJob.Status.FAILED
        else:
            job.status = ScrapeJob.Status.COMPLETED
            
        job.completed_at = timezone.now()
        job.save(update_fields=['status', 'completed_at', 'error_log'])

    except Exception as e:
        job.status = ScrapeJob.Status.FAILED
        job.error_log += f'\nFATAL: {getattr(e, "msg", str(e))}'
        job.save(update_fields=['status', 'error_log'])

    finally:
        if hasattr(conn, 'driver') and conn.driver is not None:
            conn.driver.quit()