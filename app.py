from flask import Flask
from pathlib import Path
import jpype
import jpype.imports
import threading
import sys
import os

app = Flask(__name__)

# Paths
BASE = Path(__file__).resolve().parent
JMB_DIR = BASE / "jmb"
JAR = JMB_DIR / "JMusicBot.jar"
CONFIG_ABS = Path("/etc/secrets/config.txt")   # your secret config path

def start_bot_once():
    """Start the JVM (JPype) and launch JMusicBot if not already running."""
    if not JAR.exists():
        raise FileNotFoundError(f"Missing bot JAR: {JAR}")
    if not CONFIG_ABS.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_ABS}")

    # Ensure bot writes files next to the JAR
    os.chdir(JMB_DIR)

    if not jpype.isJVMStarted():
        # JVM args
        jvm_args = [
            "-ea",
            "-Dnogui=true",                      # ensure headless
            f"-Dconfig={str(CONFIG_ABS)}",       # absolute config path
            f"-Djava.class.path={JAR.resolve()}",
        ]
        jpype.startJVM(*jvm_args)

    # Java classes we need
    JMusicBot   = jpype.JClass("com.jagrosh.jmusicbot.JMusicBot")
    Thread      = jpype.JClass("java.lang.Thread")
    ClassLoader = jpype.JClass("java.lang.ClassLoader")

    def run_main():
        try:
            # IMPORTANT: set context ClassLoader so Typesafe Config can find resources
            Thread.currentThread().setContextClassLoader(ClassLoader.getSystemClassLoader())
            # Equivalent to: java -Dconfig=/etc/secrets/config.txt -Dnogui=true -jar JMusicBot.jar
            JMusicBot.main([])  # add CLI flags if needed
        except Exception as e:
            print(f"[JMusicBot ERROR] {e}", file=sys.stderr)

    # Run bot on a daemon thread so container can shut down cleanly
    threading.Thread(target=run_main, name="JMusicBotMain", daemon=True).start()

# Start bot at import time (when Gunicorn loads the app)
try:
    start_bot_once()
except Exception as e:
    print(f"[BOOT ERROR] {e}", file=sys.stderr)

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.get("/")
def root():
    return "JMusicBot via JPype is running. Check logs for JDA status.", 200
