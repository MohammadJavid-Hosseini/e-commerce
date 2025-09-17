FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBITECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /e-commerce

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv

COPY requirements.txt /e-commerce/
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.13-slim
ENV PYTHONDONTWRITEBITECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"
   
WORKDIR /e-commerce

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /venv /venv
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]