FROM python:3.11-slim

# Install Java 17 (available on Debian trixie)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/render/project/src
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD gunicorn -b 0.0.0.0:$PORT app:app
