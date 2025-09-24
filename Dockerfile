FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install a modern JRE (Debian trixie ships OpenJDK 21)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/render/project/src

# Copy app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Quick sanity check
RUN java -version && python --version

# Gunicorn keeps the process in foreground; JMusicBot runs inside this process via JPype
CMD gunicorn -b 0.0.0.0:$PORT app:app
