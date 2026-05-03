# =============================================================================
#  discord_bot.py — MINNAL Core Entry Point
# =============================================================================

import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import config
import logger as log

# Attempt to import Persistent Views
try:
    from cogs.tickets import TicketStarter, CloseTicket
    from cogs.verify import VerifyView
except ImportError:
    TicketStarter, CloseTicket, VerifyView = None, None, None

load_dotenv()

# ── BOT INSTANCE ──────────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# ── MODULE REGISTRY ───────────────────────────────────────────────────────────
COGS = [
    'cogs.dashboard', 'cogs.admin', 'cogs.music', 'cogs.fun',
    'cogs.info', 'cogs.economy', 'cogs.giveaways', 'cogs.utilities',
    'cogs.voice_manager', 'cogs.web_bridge', 'cogs.rizz_engine',
    'cogs.voice_features', 'cogs.memes',
    'cogs.verify', 'cogs.autorole', 'cogs.ghostping',
    'cogs.stats', 'cogs.tickets', 'cogs.sentinel', 'cogs.codepilot',
    'cogs.log_relay', 'cogs.welcome', 'cogs.anime', 'cogs.levels', 'cogs.help',
    'cogs.watchlist',
    'cogs.ai_chat',
]

COG_DESC = {
    'cogs.dashboard':      'Web admin panel & API server',
    'cogs.admin':          'Server control center',
    'cogs.music':          'Voice & music player',
    'cogs.fun':            'Fun commands & games',
    'cogs.info':           'Bot info & command directory',
    'cogs.economy':        'Virtual economy & coins',
    'cogs.giveaways':      'Giveaway system',
    'cogs.utilities':      'Utility tools & reminders',
    'cogs.voice_manager':  'Dynamic voice domains',
    'cogs.web_bridge':     'Webhook & stats bridge',
    'cogs.rizz_engine':    'Status rotation engine',
    'cogs.voice_features': 'Anime voice spells',
    'cogs.memes':          'Auto meme poster',
    'cogs.verify':         'Member verification',
    'cogs.autorole':       'Auto role assignment',
    'cogs.ghostping':      'Ghost ping detector',
    'cogs.stats':          'Server statistics',
    'cogs.tickets':        'Ticket system',
    'cogs.sentinel':       'Server sentinel guard',
    'cogs.codepilot':      'AI code assistant',
    'cogs.log_relay':      'Railway → Discord log relay',
    'cogs.welcome':        'Welcome & goodbye system',
    'cogs.anime':          'Anime search & daily posts',
    'cogs.levels':         'XP & level system',
    'cogs.help':           'Command catalogue',
    'cogs.watchlist':      'Personal anime watchlist',
    'cogs.ai_chat':        'Claude AI chat channel',
}

# ── STARTUP & SYNC ────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    if all([TicketStarter, CloseTicket, VerifyView]):
        bot.add_view(TicketStarter())
        bot.add_view(CloseTicket())
        bot.add_view(VerifyView())

    try:
        synced = await bot.tree.sync()
    except Exception as e:
        log.error("SYNC", str(e))
        synced = []

    log.ready(
        bot=str(bot.user),
        guilds=len(bot.guilds),
        commands=len(synced),
        latency=f"{round(bot.latency * 1000)}ms"
    )

# ── MAIN EXECUTION ────────────────────────────────────────────────────────────

async def main():
    log.banner()

    async with bot:
        log.section(f"Loading {len(COGS)} modules")

        ok_count, fail_count = 0, 0
        for cog in COGS:
            tag  = cog.split(".")[-1]
            desc = COG_DESC.get(cog, "")
            try:
                await bot.load_extension(cog)
                log.ok(tag, desc)
                ok_count += 1
            except Exception as e:
                log.fail(tag, str(e)[:65])
                fail_count += 1

        print()
        if fail_count:
            log.warn("MODULES", f"{ok_count} loaded  │  {fail_count} failed")
        else:
            log.ok("ALL MODULES", f"{ok_count} loaded with no errors ✓")
        print()

        TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n  [OFFLINE]  Shutdown complete.\n")
