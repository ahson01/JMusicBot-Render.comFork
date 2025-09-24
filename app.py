from flask import Flask, jsonify, request
from pathlib import Path
import subprocess, shlex

app = Flask(__name__)

BASE = Path(__file__).resolve().parent
JMB_DIR = BASE / "jmb"
JAR = JMB_DIR / "JMusicBot.jar"
CONFIG = JMB_DIR / "config.txt"

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.post("/start-bot")
def start_bot():
    """
    Starts JMusicBot, using the config in ./jmb/config.txt.
    Runs with cwd=JMB_DIR so any files the bot writes end up in ./jmb.
    """
    if not JAR.exists():
        return jsonify({"error": f"Missing {JAR}"}), 500
    if not CONFIG.exists():
        return jsonify({"error": f"Missing {CONFIG}"}), 500

    # You can pass additional JVM or bot args via JSON if you want:
    extra_args = request.json.get("args", []) if request.is_json else []
    if not isinstance(extra_args, list):
        return jsonify({"error": "args must be a list"}), 400

    cmd = ["java", "-Dconfig=/etc/secrets/.env", "-jar", str(JAR), *extra_args]

    # Important: cwd=JMB_DIR so relative paths go next to the jar
    proc = subprocess.Popen(
        cmd,
        cwd=str(JMB_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # Don't block; just acknowledge it started
    return jsonify({"pid": proc.pid, "cmd": " ".join(map(shlex.quote, cmd))}), 202

@app.post("/stop-bot")
def stop_bot():
    # Super minimal example: find java process for the JAR and kill it.
    # In production, track the Popen handle or use a supervisor.
    try:
        subprocess.run(
            ["bash", "-lc", "pkill -f JMusicBot.jar || true"],
            check=False
        )
        return jsonify({"stopped": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
