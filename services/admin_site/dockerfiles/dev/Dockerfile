FROM python:3.11-slim

# Set labels for maintainer information
LABEL maintainer="amingholami06@gmail.com"

# Prevent python from writing pyc files and buffer output
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies if any (e.g., for psycopg2)
# RUN apt-get update && apt-get install -y ...

# Install python dependencies
# Copy only the requirements file first to leverage Docker cache
COPY ./requirements/dev/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . .