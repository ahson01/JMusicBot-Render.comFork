FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install Java 21 (available on Debian trixie)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/render/project/src
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Optional sanity check (shows up in build logs)
RUN java -version && python --version

CMD gunicorn -b 0.0.0.0:$PORT app:app
