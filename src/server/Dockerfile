FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY src/server/requirements.txt /app/src/server/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/src/server/requirements.txt

COPY . /app

EXPOSE 5000

ENV FLASK_APP=src/server/app.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
