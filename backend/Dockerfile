# ── Stage 1: Python + Chrome ─────────────────────────────────
FROM python:3.12-slim

# Install Chrome + ChromeDriver + Tesseract (for captcha)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    tesseract-ocr \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Tell your scraper to use the system Chrome instead of webdriver-manager
ENV CHROME_DRIVER=/usr/bin/chromedriver
ENV CHROME_BINARY=/usr/bin/chromium
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/base.txt \
    && pip install --no-cache-dir gunicorn

# Copy source
COPY . .

# collectstatic runs at container startup (needs SECRET_KEY from .env)
# NOT here at build time