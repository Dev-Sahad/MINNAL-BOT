# =============================================================================
#  logger.py — MINNAL Clean Log Formatter
#  Used across all cogs for consistent, readable Railway deploy logs
# =============================================================================

import sys
from datetime import datetime, timezone

# ── ANSI (Railway supports these) ─────────────────────────────────────────
R  = "\033[0m"       # reset
B  = "\033[1m"       # bold
D  = "\033[2m"       # dim
G  = "\033[32m"      # green
RE = "\033[31m"      # red
Y  = "\033[33m"      # yellow
C  = "\033[36m"      # cyan
P  = "\033[35m"      # purple
W  = "\033[37m"      # white

WIDTH = 58

def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

# ── Startup chrome ─────────────────────────────────────────────────────────

def banner():
    bar = "━" * WIDTH
    print(f"\n{B}{P}{bar}{R}")
    print(f"{B}{P}  ⚡  MINNAL BOT  │  Railway Deployment{R}")
    print(f"{B}{P}{bar}{R}\n", flush=True)

def section(title: str):
    print(f"{D}  {'─' * (WIDTH - 2)}{R}")
    print(f"{B}  {title}{R}")
    print(f"{D}  {'─' * (WIDTH - 2)}{R}", flush=True)

def ready(bot: str, guilds: int, commands: int, latency: str):
    bar = "━" * WIDTH
    print(f"\n{B}{G}{bar}{R}")
    print(f"{B}{G}  ✅  ONLINE  —  {bot}{R}")
    print(f"{D}  {'─' * (WIDTH - 2)}{R}")
    print(f"  {B}{'Guilds':<12}{R}{guilds}")
    print(f"  {B}{'Commands':<12}{R}{commands} synced")
    print(f"  {B}{'Latency':<12}{R}{latency}")
    print(f"{B}{G}{bar}{R}\n", flush=True)

# ── Cog table rows ─────────────────────────────────────────────────────────

def ok(tag: str, desc: str = ""):
    print(f"  {G}✓{R}  {B}{tag:<18}{R}  {D}{desc}{R}", flush=True)

def fail(tag: str, msg: str = ""):
    print(f"  {RE}✗{R}  {B}{tag:<18}{R}  {RE}{msg}{R}", flush=True)

def warn(tag: str, msg: str = ""):
    print(f"  {Y}⚠{R}  {B}{tag:<18}{R}  {Y}{msg}{R}", flush=True)

# ── Runtime event logs (used by cogs) ──────────────────────────────────────

def event(module: str, msg: str):
    ts  = _ts()
    tag = f"[{module.upper()}]"
    print(f"  {D}{ts}{R}  {C}{tag:<12}{R}  {msg}", flush=True)

def error(module: str, msg: str):
    ts  = _ts()
    tag = f"[{module.upper()}]"
    print(f"  {D}{ts}{R}  {RE}{tag:<12}{R}  {RE}{msg}{R}", flush=True)

def warning(module: str, msg: str):
    ts  = _ts()
    tag = f"[{module.upper()}]"
    print(f"  {D}{ts}{R}  {Y}{tag:<12}{R}  {Y}{msg}{R}", flush=True)
