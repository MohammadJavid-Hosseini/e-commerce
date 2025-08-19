FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBITECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv

COPY requirements.txt /app/
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.13-slim
ENV PYTHONDONTWRITEBITECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"
   
WORKDIR /app
COPY --from=builder /venv /venv
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]