import os
import json
import uuid
import socket

import redis
from flask import Flask, request, make_response, render_template_string

OPTION_A = "Docker Compose"
OPTION_B = "Kubernetes"

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

PAGE = """
<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Votación</title>
<style>
 body{font-family:Arial,sans-serif;background:#f4f6f8;text-align:center;padding:40px}
 h1{color:#1d3557} .box{display:inline-block;background:#fff;padding:30px 40px;border-radius:12px;box-shadow:0 2px 8px #0002}
 button{font-size:20px;margin:10px;padding:14px 28px;border:0;border-radius:8px;color:#fff;cursor:pointer}
 .a{background:#2a9d8f} .b{background:#e76f51} small{color:#666}
</style></head><body><div class="box">
<h1>¿Cuál prefiere para orquestar contenedores?</h1>
<form method="POST">
 <button class="a" name="vote" value="{{a}}">{{a}}</button>
 <button class="b" name="vote" value="{{b}}">{{b}}</button>
</form>
{% if voted %}<p>✅ Su voto actual: <b>{{voted}}</b></p>{% endif %}
<small>Contenedor: {{host}}</small>
</div></body></html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    voter_id = request.cookies.get("voter_id") or uuid.uuid4().hex
    voted = None
    if request.method == "POST":
        voted = request.form["vote"]
        if voted in (OPTION_A, OPTION_B):
            r.rpush("votes", json.dumps({"voter_id": voter_id, "vote": voted}))
    resp = make_response(render_template_string(
        PAGE, a=OPTION_A, b=OPTION_B, voted=voted, host=socket.gethostname()))
    resp.set_cookie("voter_id", voter_id)
    return resp

@app.route("/health")
def health():
    return {"status": "ok"}
