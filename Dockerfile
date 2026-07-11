FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/base.txt
COPY . /app/
RUN mkdir -p /app/static /app/media \
    && adduser -D appuser \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000