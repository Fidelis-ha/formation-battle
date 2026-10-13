#!/usr/bin/env python3
"""Deployed index.html als statisches Vercel-Deployment (REST, Token aus .env)."""
import base64, json, os, sys, urllib.request

BASE = "/opt/data/projekte/formation-battle"
TEAM = "team_U1752pwn4ZmXXEvWo0gIt6q1"
NAME = "formation-battle"

def env_token():
    for line in open("/opt/data/.env"):
        if line.startswith("VERCEL_API_TOKEN="):
            return line.strip().split("=", 1)[1].strip().strip('"')
    sys.exit("VERCEL_API_TOKEN nicht gefunden")

def api(path, payload, token):
    url = f"https://api.vercel.com{path}?teamId={TEAM}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "kairos-deploy"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

token = env_token()
html = open(f"{BASE}/index.html", "rb").read()
sha1 = __import__("hashlib").sha1(html).hexdigest()
res = api("/v13/deployments", {
    "name": NAME,
    "files": [{"file": "index.html", "data": base64.b64encode(html).decode(), "encoding": "base64"}],
    "projectSettings": {"framework": None},
    "target": "production",
}, token)
print("Deployment angelegt:", res.get("uid"), res.get("url"))
