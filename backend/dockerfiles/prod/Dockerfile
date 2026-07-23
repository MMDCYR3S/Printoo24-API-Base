FROM python:3.11-slim

LABEL maintainer="mddcyres@gmail.com"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# نصب پیش‌نیازها با استفاده از آینه ایران (برای سرعت بیشتر در سرور داخلی)
RUN sed -i 's/deb.debian.org/mirror.arvancloud.ir/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend/requirements/dev/requirements.txt /app/requirements.txt

# نصب کتابخانه‌ها و اضافه کردن gunicorn برای پروداکشن
RUN pip install --no-cache-dir -r /app/requirements.txt && pip install gunicorn

COPY ./backend /app
WORKDIR /app

EXPOSE 9010

# دستور اجرا برای پروداکشن (به جای runserver)
CMD ["gunicorn", "--bind", "0.0.0.0:9010", "--workers", "3", "backend.wsgi:application"]