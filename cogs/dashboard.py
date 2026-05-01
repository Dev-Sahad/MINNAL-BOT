# =============================================================================
#  cogs/dashboard.py — Web Panel + Live Config Save
# =============================================================================

import discord
from discord.ext import commands
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import psutil
import time
import os
import json


DATA_DIR = "data"
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "bot": {"name": "MINNAL", "tagline": "The Lightning Engine", "developer": "Sahad", "embed_color": "#9b59b6"},
    "welcome": {"enabled": True, "channel_id": "", "title": "Welcome!", "message": "Hey {member}!", "image_url": ""},
    "summon": {"enabled": True, "trigger_channel_id": "", "domain_names": ["Minnal Cave", "Sukuna's Shrine", "Gojo's Infinity"]},
    "voices": {"enabled": True, "voice_list": [
        {"spell": "Domain Expansion!", "anime": "Sukuna", "voice_text": "Domain Expansion!", "audio_file": ""},
        {"spell": "Rasengan!", "anime": "Naruto", "voice_text": "Rasengan!", "audio_file": ""}
    ]},
    "bio": {"rotation_minutes": 5, "statuses": [{"type": "watching", "name": "Server"}]},
    "memes": {"enabled": True, "channel_id": "", "troll_messages": ["{target} got trolled!"]},
    "economy": {"currency_name": "Coins", "currency_symbol": "⚡", "starting_balance": 100, "daily_reward": 100, "weekly_reward": 1000},
    "music": {"enabled": True, "default_source": "soundcloud", "max_queue_size": 50}
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
        PORT = int(os.getenv('PORT', 8080))
        config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="error")
        server = uvicorn.Server(config)
        try:
            print(f"🌐 Web Panel on port {PORT}", flush=True)
            await server.serve()
        except Exception as e:
            print(f"❌ Server error: {e}", flush=True)


@app.get("/", response_class=HTMLResponse)
async def panel():
    if os.path.exists("advanced-admin-panel.html"):
        with open("advanced-admin-panel.html", 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Panel not found</h1>")


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


async def setup(bot):
    await bot.add_cog(Dashboard(bot))
