FROM python:3.11-slim

# Install Java 11 (required by JMusicBot)
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-11-jre-headless \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/render/project/src
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Render provides $PORT; bind gunicorn to it
CMD gunicorn -b 0.0.0.0:$PORT app:app
