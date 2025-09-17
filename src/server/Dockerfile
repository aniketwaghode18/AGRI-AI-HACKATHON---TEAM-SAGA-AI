# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY src/server/requirements.txt /app/src/server/requirements.txt
RUN pip install --no-cache-dir -r /app/src/server/requirements.txt

COPY . /app

ENV FLASK_ENV=production
ENV MOCK=1
EXPOSE 5000
CMD ["python", "src/server/app.py"]
