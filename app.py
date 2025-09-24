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
CONFIG_ABS = Path("/etc/secrets/config.txt")   # absolute config path from Render secret file

def start_bot_once():
    """Start the JVM and JMusicBot if not already running."""
    if not JAR.exists():
        raise FileNotFoundError(f"Missing bot JAR: {JAR}")
    if not CONFIG_ABS.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_ABS}")

    # Switch cwd so any files JMusicBot writes end up in ./jmb
    os.chdir(JMB_DIR)

    if not jpype.isJVMStarted():
        # JVM args: enable assertions, point to config, set classpath
        jvm_args = [
            "-ea",
            f"-Dconfig={str(CONFIG_ABS)}",
            f"-Djava.class.path={JAR.resolve()}",
        ]
        jpype.startJVM(*jvm_args)

    # Import main class from the JAR
    JMusicBot = jpype.JClass("com.jagrosh.jmusicbot.JMusicBot")

    def run_main():
        try:
            # Launch the bot (equivalent to: java -Dconfig=/etc/secrets/config.txt -jar JMusicBot.jar)
            JMusicBot.main([])  # add flags here if needed, e.g. ["--nogui"]
        except Exception as e:
            print(f"[JMusicBot ERROR] {e}", file=sys.stderr)

    # Start bot in a daemon thread so the container can shut down cleanly
    threading.Thread(target=run_main, name="JMusicBotMain", daemon=True).start()

# Start the bot at import time (so it runs as soon as Gunicorn loads the app)
try:
    start_bot_once()
except Exception as e:
    print(f"[BOOT ERROR] {e}", file=sys.stderr)

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.get("/")
def root():
    return "JMusicBot via JPype is running. Check logs for details.", 200
