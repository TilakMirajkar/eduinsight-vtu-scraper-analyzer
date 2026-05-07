from django.contrib import admin
from .models import ScrapeJob, SkippedUSN

admin.site.register(ScrapeJob)
admin.site.register(SkippedUSN)