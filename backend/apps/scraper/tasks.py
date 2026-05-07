from celery import shared_task
from django.utils import timezone
from selenium.common.exceptions import UnexpectedAlertPresentException
from apps.scraper.models import ScrapeJob, SkippedUSN
from apps.scraper.services.scraper import Connection
from apps.analyzer.services.processor import save_scraped_results

@shared_task
def scrape_task(job_id):
    job = ScrapeJob.objects.get(id=job_id)
    conn = Connection()
    soup_dict = {}
    total = len(job.usn_sequence)
    abort = False
    cool_counter = 0

    try:
        job.status = ScrapeJob.Status.RUNNING
        job.save()

        conn.connect(job.result_url, mode=False)

        for i, num in enumerate(job.usn_sequence):
            usn = f'{job.usn_prefix}{num:03d}'
            this_retry = 0

            while this_retry < job.retry_count:
                try:
                    conn.enter_usn(usn)

                    captcha_text, error = conn.get_captcha()

                    if error:
                        job.error_log += 'Error! Tesseract not configured. Retry after configuring.'
                        job.save()
                        abort = True
                        break

                    elif len(captcha_text) != 6:
                        job.error_log += 'Invalid captcha. Trying again.\n'
                        job.save()
                        conn.driver.refresh()
                        continue
                    
                    else:
                        conn.captcha_submit(captcha_text)
                        conn.sleep(0.01)

                    soup_dict = conn.get_info(soup_dict)

                    job.error_log += f'Data collected for {usn}\n'
                    cool_counter = 0
                    job.progress = int((i + 1) / total * 100)
                    job.save()

                    conn.sleep(2)
                    conn.driver.get(job.result_url)

                except UnexpectedAlertPresentException:
                    alert = conn.check_alert()
                    alert_text = alert.text

                    job.error_log += f'Error for {usn}: {alert_text}\n'
                    job.save()

                    if alert_text == 'University Seat Number is not available or Invalid..!' or alert_text == 'You have not applied for reval or reval results are awaited !!!':
                        cool_counter += 1
                        job.error_log += f'Moving to the next USN.\n'
                        job.save()
                        SkippedUSN.objects.create(job=job, usn=usn, reason=alert_text)
                        alert.accept()
                        break

                    elif alert_text == '':
                        job.error_log += f'\nUnfortunately, this IP address has been blocked due to excessive requests in a short period of time.\nYou will not be able to access this particular link using this IP address anymore.\nUse an internet connection with a different IP address or set a proxy server in your system settings.\n'
                        job.save()
                        abort = True
                        alert.accept()
                        break
                    else:
                        cool_counter += 1
                        job.error_log += 'Trying again.\n'
                        job.save()
                        alert.accept() 

                except Exception:
                    this_retry += 1
                    conn.sleep(job.retry_delay)
                    conn.driver.refresh()

            if abort:
                break

        if soup_dict:
            save_scraped_results(job, soup_dict)

        job.status = ScrapeJob.Status.COMPLETED
        job.completed_at = timezone.now()
        job.save()

    except Exception as e:
        job.status = ScrapeJob.Status.FAILED
        job.error_log = str(e)
        job.save()

    finally:
        conn.driver.quit()