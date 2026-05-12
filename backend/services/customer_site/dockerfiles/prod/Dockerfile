FROM python:3.11-slim

LABEL maintainer="mddcyres@gmail.com"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# نصب پیش‌نیازها از مخازن اصلی دیبیان
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend/shared_libs /app/shared_libs
COPY ./backend/services/customer_site/requirements/dev/requirements.txt /app/requirements.txt

# نصب کتابخانه‌ها و اضافه کردن gunicorn برای پروداکشن
RUN pip install --no-cache-dir -r /app/requirements.txt && pip install gunicorn

COPY ./backend/services/customer_site /app/src
WORKDIR /app/src

EXPOSE 9010

# دستور اجرا برای پروداکشن (به جای runserver)
CMD ["gunicorn", "--bind", "0.0.0.0:9010", "--workers", "3", "customer_site.wsgi:application"]
