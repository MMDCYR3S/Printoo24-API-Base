FROM python:3.11-slim

# ===== نام گذاری داکر فایل ===== #
LABEL maintainer="amingholami06@gmail.com"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ===== مسیر پوشه ===== #
WORKDIR /app

# ===== نصب پیش نیاز اصلی داکر ===== #
RUN sed -i 's/deb.debian.org/mirror.arvancloud.ir/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# ===== نصب و کپی اپلیکیشن مشترک ===== #
COPY ./backend/shared_libs /app/shared_libs

# ===== نصب و کپی اپلیکیشن مشتری سایت ===== #
COPY ./backend/services/customer_site/requirements/prod/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# نصب Gunicorn
RUN pip install --no-cache-dir gunicorn

# ===== کپی سورس کد اپلیکیشن مشتری سایت ===== #
COPY ./backend/services/customer_site /app/src
WORKDIR /app/src

# ===== ساخت پوشه logs ===== #
RUN mkdir -p /app/src/logs

# ===== جمع‌آوری Static Files ===== #
RUN python manage.py collectstatic --noinput --settings=customer_site.settings.production || true

# ===== پورت پیش فرض ===== #
EXPOSE 9010

# ===== دستور اجرای پیش فرض با Gunicorn ===== #
CMD ["gunicorn", "customer_site.wsgi:application", "--bind", "0.0.0.0:9010", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]