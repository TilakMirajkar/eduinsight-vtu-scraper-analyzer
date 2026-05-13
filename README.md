# EduInsight — VTU Results Scraper & Analyzer

A full-stack web application that automates the scraping and analysis of VTU (Visvesvaraya Technological University) exam results. Submit a batch of USNs, let the system scrape results in the background, and download a subject-wise Excel report with SGPA scores and pass percentage charts.

---

## Features

### Scraping
- Submit a USN prefix + range (e.g. `2AG21CS` + `1-60`) and a VTU result URL
- Supports ranges (`1-60`), comma lists (`1,2,5`), and mixed formats (`1,3-10,15`)
- Runs in the background via Celery — no waiting on the browser
- Live progress polling — watch each job update in real time
- Automatic CAPTCHA solving using image processing + Tesseract OCR
- Configurable retry count and delay for failed USNs
- Supports both regular and revaluation result pages (auto-detected from URL)
- Multiple jobs can run simultaneously

### Analysis
- Trigger analysis on any completed scrape job
- Generates a subject-wise Excel report with marks, grades, and results per student
- Calculates SGPA for every student
- Produces a pass percentage bar chart per subject
- Download Excel and chart directly from the UI

### Jobs Dashboard
- View all scrape jobs with live status, progress bar, and USN count
- Per-job log viewer for debugging failed USNs
- One-click trigger to analyze a completed job
- Download buttons appear automatically once analysis is done

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, shadcn/ui, TanStack Query |
| Backend | Django 5, Django REST Framework |
| Task Queue | Celery |
| Broker / Cache | Redis |
| Database | PostgreSQL |
| Scraping | Selenium, Chromium, BeautifulSoup |
| OCR | Tesseract |
| Reports | openpyxl, matplotlib, pandas |
| Deployment | Docker, Docker Compose, Nginx |

---

## Project Structure

```
vtu-scraper-analyzer/
├── backend/
│   ├── apps/
│   │   ├── scraper/          # Scraping logic, Celery tasks, models
│   │   └── analyzer/         # Analysis logic, report generation, models
│   ├── config/
│   │   ├── settings/         # base / development / production
│   │   └── celery.py
│   ├── core/                 # Global exception handler
│   ├── requirements/         # base / development / production
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios client + API functions
│   │   ├── components/       # Navbar, shadcn UI components
│   │   ├── hooks/            # TanStack Query hooks
│   │   └── pages/            # ScrapePage, AnalyzePage
│   ├── nginx.conf
│   └── Dockerfile
└── docker-compose.yml
```

---

## Getting Started

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone the repo

```bash
git clone https://github.com/TilakMirajkar/vtu-scraper-analyzer.git
cd vtu-scraper-analyzer
```

### 2. Set up environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and fill in your values:

```dotenv
SECRET_KEY=your-secret-key-here

DB_NAME=vtu_db
DB_USER=vtu_user
DB_PASSWORD=your-strong-password
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0

DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1
```

Then copy it to the repo root (Docker Compose reads `.env` from where you run it):

```bash
cp backend/.env .env
```

### 3. Build and start

```bash
docker compose up --build
```

The first run will pull images, install dependencies, run migrations, and start all services. This takes a few minutes.

### 4. Open the app

| Service | URL |
|---|---|
| App | http://localhost |
| Django Admin | http://localhost/admin/ |

---

## Usage

### Scrape results

1. Go to the **Scrape** tab
2. Enter a USN prefix (e.g. `2AG21CS`), a range (e.g. `1-60`), select the semester, and paste the VTU result URL
3. Click **Start the automated process**
4. Watch progress live — the job runs in the background

### Analyze results

1. Go to the **Analyze** tab
2. Find your completed job in the table
3. Click the **analyze icon** on that row
4. Once done, download the Excel report and/or the pass percentage chart

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DB_NAME` | PostgreSQL database name | `vtu_db` |
| `DB_USER` | PostgreSQL username | `vtu_user` |
| `DB_PASSWORD` | PostgreSQL password | `strongpassword` |
| `DB_HOST` | Database host | `db` (Docker) / `localhost` (local) |
| `DB_PORT` | Database port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `DJANGO_SETTINGS_MODULE` | Settings module to use | `config.settings.development` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |

---

## Docker Services

| Service | Description |
|---|---|
| `db` | PostgreSQL 16 database |
| `redis` | Redis 7 broker for Celery |
| `backend` | Django + Gunicorn API server |
| `worker` | Celery worker with Chromium for scraping |
| `frontend` | React app served via Nginx (also reverse-proxies `/api/`) |

### Useful commands

```bash
# Start in background
docker compose up -d

# View logs
docker compose logs -f worker     # scraping logs
docker compose logs -f backend    # API logs

# Stop everything
docker compose down

# Stop and wipe the database
docker compose down -v

# Open a Django shell
docker compose exec backend python manage.py shell
```

---

## Notes

- The scraper uses **headless Chromium** inside the worker container — no display needed
- CAPTCHA images are processed locally using Tesseract — no external API calls
- `is_reval` is auto-detected from the result URL (checks for `RV` in the URL)
- All generated Excel files and chart images are stored in a shared Docker volume (`media_files`)