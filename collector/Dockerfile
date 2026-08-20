# Metrics Collector image: Python + Flask on port 6000.

# If you want to build the image from a pre-built own collector:1.0.0 image, uncomment the following line and comment out the next line.
# FROM collector:1.0.0
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py metrics.py ./

EXPOSE 6000
CMD ["python", "app.py"]
