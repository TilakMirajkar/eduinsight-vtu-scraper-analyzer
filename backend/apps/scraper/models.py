from django.db import models

# Create your models here.
class ScrapeJob(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        RUNNING = 'running'
        COMPLETED = 'completed'
        FAILED = 'failed'

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    progress = models.IntegerField(default=0)
    usn_prefix = models.CharField(max_length=7)
    usn_sequence = models.JSONField()
    exam_semester = models.IntegerField()
    result_url = models.CharField(max_length=255)
    is_reval = models.BooleanField(default=False)
    error_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    retry_delay = models.IntegerField(default=5)
    retry_count = models.IntegerField(default=5)

    def __str__(self):
        return f"Job {self.id} — {self.usn_prefix} | Sem {self.exam_semester} ({self.status})"

class SkippedUSN(models.Model):
    job = models.ForeignKey(ScrapeJob, on_delete=models.CASCADE)
    usn = models.CharField(max_length=10)
    reason = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.usn} skipped — {self.reason}"
