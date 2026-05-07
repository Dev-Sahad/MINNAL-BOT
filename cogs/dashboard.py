# =============================================================================
#  cogs/dashboard.py — Web Panel + Live Config Save
# =============================================================================

import discord
from discord.ext import commands
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import psutil
import time
import os
import json
import subprocess
import base64
import requests as req_lib


DATA_DIR = "data"
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "bot": {"name": "MINNAL", "tagline": "The Lightning Engine", "developer": "Sahad", "embed_color": "#9b59b6", "prefix": "/"},
    "channels": {
        "welcome_channel_id": "", "leave_channel_id": "", "music_channel_id": "",
        "ticket_channel_id": "", "game_update_channel_id": "", "meme_channel_id": "",
        "log_channel_id": "", "announcement_channel_id": "", "giveaway_channel_id": "",
        "default_voice_channel_id": "", "announcement_voice_channel_id": ""
    },
    "roles": {
        "verified_role_id": "", "unverified_role_id": "", "staff_role_id": "",
        "muted_role_id": "", "bot_role_id": "", "member_role_id": ""
    },
    "welcome": {"enabled": True, "channel_id": "", "title": "Welcome!", "message": "Hey {member}!", "image_url": "", "leave_enabled": True, "leave_message": "Goodbye {member}!", "leave_image_url": ""},
    "dm_join": {"enabled": True, "message": "👋 Hey **{member}**, welcome to **{server}**!\n\nPlease verify your account to join the fam! 🎉"},
    "verify": {"enabled": True, "channel_id": "", "verified_role_id": "", "unverified_role_id": "", "message": "Click the button below to verify!", "button_label": "✅ Verify"},
    "tickets": {"enabled": True, "channel_id": "", "staff_role_id": "", "category_id": "", "welcome_message": "Hello {user}! Our staff will assist you shortly.", "close_message": "Ticket closed.", "log_channel_id": ""},
    "autorole": {"enabled": False, "role_ids": [], "bot_role_id": ""},
    "giveaways": {"enabled": True, "manager_role_id": "", "default_duration_hours": 24, "default_winners": 1},
    "summon": {"enabled": True, "trigger_channel_id": "", "domain_names": ["Minnal Cave", "Sukuna's Shrine", "Gojo's Infinity"]},
    "voices": {"enabled": True, "voice_list": [
        {"spell": "Domain Expansion!", "anime": "Sukuna", "voice_text": "Domain Expansion!", "audio_file": ""},
        {"spell": "Rasengan!", "anime": "Naruto", "voice_text": "Rasengan!", "audio_file": ""}
    ]},
    "bio": {"rotation_minutes": 5, "statuses": [{"type": "watching", "name": "Server"}]},
    "memes": {"enabled": True, "channel_id": "", "troll_messages": ["{target} got trolled!"]},
    "economy": {"currency_name": "Coins", "currency_symbol": "⚡", "starting_balance": 100, "daily_reward": 100, "weekly_reward": 1000, "rob_enabled": True, "gamble_enabled": True},
    "music": {"enabled": True, "default_source": "soundcloud", "max_queue_size": 50, "channel_id": "", "dj_role_id": "", "volume": 100},
    "sentinel": {"enabled": True, "log_channel_id": "", "anti_spam": True, "anti_raid": True, "anti_link": False, "warn_limit": 3, "mute_duration_minutes": 10},
    "ghost_ping": {"enabled": True, "log_channel_id": "", "alert_message": "👻 {user} ghost pinged {target}!"},
    "codepilot": {"enabled": True, "allowed_channel_ids": [], "max_response_length": 2000}
}


def ensure_dirs():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_settings():
    ensure_dirs()
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key in DEFAULT_SETTINGS:
                    if key not in data:
                        data[key] = DEFAULT_SETTINGS[key]
                return data
        else:
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS
    except Exception as e:
        print(f"Settings load error: {e}", flush=True)
        return DEFAULT_SETTINGS.copy()


def save_settings(data):
    ensure_dirs()
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ Settings saved", flush=True)
        return True
    except Exception as e:
        print(f"❌ Save error: {e}", flush=True)
        return False


# FastAPI
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

bot_instance = None
start_time = time.time()


class LoginReq(BaseModel):
    password: str


class SaveReq(BaseModel):
    section: str
    data: Dict[str, Any]


def check_auth(auth):
    if not auth or not auth.startswith('Bearer '):
        return False
    return auth[7:] == os.getenv('ADMIN_PASSWORD', 'MINNAL@2025')


class Dashboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global bot_instance
        bot_instance = bot
        self.bg_task = self.bot.loop.create_task(self.run_server())

    async def run_server(self):
        PORT = int(os.getenv('PORT', 6000))
        config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="error")
        server = uvicorn.Server(config)
        try:
            print(f"🌐 Web Panel on port {PORT}", flush=True)
            await server.serve()
        except Exception as e:
            print(f"❌ Server error: {e}", flush=True)


@app.get("/api/test")
async def test():
    return {"status": "working", "settings_exists": os.path.exists(SETTINGS_FILE)}


@app.post("/api/login")
async def login(req: LoginReq):
    expected = os.getenv('ADMIN_PASSWORD', 'MINNAL@2025')
    if req.password == expected:
        return {"success": True, "token": expected}
    raise HTTPException(status_code=401, detail="Wrong password")


@app.get("/api/config")
async def get_cfg(authorization: Optional[str] = Header(None)):
    if not check_auth(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"success": True, "config": load_settings()}


@app.post("/api/save")
async def save_section(req: SaveReq, authorization: Optional[str] = Header(None)):
    if not check_auth(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    settings = load_settings()
    settings[req.section] = req.data
    
    if save_settings(settings):
        return {"success": True}
    raise HTTPException(status_code=500, detail="Save failed")


GITHUB_OWNER = "Dev-Sahad"
GITHUB_REPO  = "MINNAL-BOT"
GITHUB_API   = "https://api.github.com"

# Files to push: (github_path, local_path)
PUSH_FILES = [
    ("data/settings.json", SETTINGS_FILE),
    ("advanced-admin-panel.html", "advanced-admin-panel.html"),
]


def _gh_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "MINNAL-Bot"
    }


def _gh_push_file(token: str, github_path: str, local_path: str, commit_msg: str) -> dict:
    """Push a single file via GitHub REST API. Returns {ok, msg}."""
    url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{github_path}"
    headers = _gh_headers(token)

    if not os.path.exists(local_path):
        return {"ok": False, "msg": f"local file not found: {local_path}"}

    with open(local_path, "r", encoding="utf-8") as f:
        raw = f.read()
    encoded = base64.b64encode(raw.encode("utf-8")).decode()

    # Get current SHA (needed for update)
    r = req_lib.get(url, headers=headers, timeout=10)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {"message": commit_msg, "content": encoded, "branch": "main"}
    if sha:
        payload["sha"] = sha

    r = req_lib.put(url, headers=headers, json=payload, timeout=15)
    if r.status_code in (200, 201):
        return {"ok": True, "msg": f"✅ {github_path}"}
    body = r.json()
    return {"ok": False, "msg": f"❌ {github_path}: {body.get('message', r.status_code)}"}


@app.post("/api/github/push")
async def github_push(authorization: Optional[str] = Header(None)):
    if not check_auth(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN', '')
    if not token:
        raise HTTPException(status_code=500, detail="GITHUB_PERSONAL_ACCESS_TOKEN not set in Railway environment variables")

    commit_msg = "⚙️ Settings update from Admin Panel"
    steps = []
    any_ok = False

    for github_path, local_path in PUSH_FILES:
        result = _gh_push_file(token, github_path, local_path, commit_msg)
        steps.append(result["msg"])
        if result["ok"]:
            any_ok = True

    if not any_ok:
        raise HTTPException(status_code=500, detail="\n".join(steps))

    return {"success": True, "message": f"Pushed to GitHub! Railway will redeploy automatically.", "steps": steps}


@app.get("/api/github/status")
async def github_status(authorization: Optional[str] = Header(None)):
    if not check_auth(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN', '')
    has_token = bool(token)
    commits = []

    if token:
        url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits?per_page=5&sha=main"
        r = req_lib.get(url, headers=_gh_headers(token), timeout=10)
        if r.status_code == 200:
            for c in r.json():
                sha = c.get("sha", "")[:7]
                msg = c.get("commit", {}).get("message", "").split("\n")[0]
                commits.append(f"{sha} {msg}")

    return {
        "success": True,
        "recent_commits": commits,
        "uncommitted_changes": None,
        "has_token": has_token
    }


@app.get("/api/stats")
async def stats():
    if not bot_instance:
        return {"online": False}
    
    uptime = int(time.time() - start_time)
    h, r = divmod(uptime, 3600)
    m, s = divmod(r, 60)
    
    return {
        "online": True,
        "latency": f"{round(bot_instance.latency * 1000)}ms",
        "uptime": f"{h}h {m}m",
        "guilds": len(bot_instance.guilds),
        "users": sum(g.member_count for g in bot_instance.guilds),
        "cpu": f"{psutil.cpu_percent()}%",
        "ram": f"{psutil.virtual_memory().percent}%"
    }


@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_file(path: str = ""):
    if not path or path == "/":
        path = "advanced-admin-panel.html"
    
    # Security: prevent directory traversal
    safe_path = os.path.basename(path)
    if not safe_path.endswith(".html") and "." not in safe_path:
        safe_path += ".html"

    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        with open(safe_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    
    # If not found, try to serve advanced-admin-panel as default
    if os.path.exists("advanced-admin-panel.html"):
        with open("advanced-admin-panel.html", 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
            
    return HTMLResponse(content="<h1>Panel not found</h1>", status_code=404)


async def setup(bot):
    await bot.add_cog(Dashboard(bot))
