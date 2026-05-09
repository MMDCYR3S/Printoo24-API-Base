FROM python:3.11-slim

# ===== نام گذاری داکر فایل ===== #
LABEL maintainer="amingholami06@gmail.com"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ===== مسیر پوشه ===== #
WORKDIR /app

# ===== نصب پیش نیاز اصلی داکر ===== #
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# ===== نصب و کپی اپلیکیشن مشترک ===== #
COPY ./backend/shared_libs /app/shared_libs

# ===== نصب و کپی اپلیکیشن مشتری سایت ===== #
COPY ./backend/services/customer_site/requirements/dev/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# ===== کپی سورس کد اپلیکیشن مشتری سایت ===== #
COPY ./backend/services/customer_site /app/src
WORKDIR /app/src

# ===== پورت پیش فرض ===== #
EXPOSE 9010

# ===== دستور اجرای پیش فرض ===== #
CMD ["python", "manage.py", "runserver", "0.0.0.0:9010"]