FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# תלותי מערכת נדרשות

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 1) התקנת הדרישות הקיימות של הפרויקט
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 2) דריסת גרסאות כדי להתאים ל-RQ 2.x (שלא ייפול עם rq_scheduler)
# django-rq 3.0.1 תומך רשמית ב-RQ 2.x
RUN pip install --no-cache-dir "django-rq==3.0.1" "rq==2.6.0" "rq-scheduler==0.14.0"

# העתקת הקוד
COPY . /app

ENV DJANGO_SETTINGS_MODULE=statuspage.settings \
    PORT=8000

# מיגרציות + סטטיק + Gunicorn
CMD sh -c "cd statuspage && \
           python manage.py migrate --noinput && \
           python manage.py collectstatic --noinput && \
           exec gunicorn statuspage.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --timeout 120"
