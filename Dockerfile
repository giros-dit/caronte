FROM python:3.12-slim

# Evita generar .pyc y fuerza el log sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y openssl wakeonlan

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir /app

COPY . /app

WORKDIR /app

EXPOSE 3000

ENTRYPOINT ["python", "wsgi.py"]