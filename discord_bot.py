# =============================================================================
#  discord_bot.py — MINNAL Core Entry Point
#  Status: omni_status module removed
# =============================================================================

import asyncio
import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
from dotenv import load_dotenv
import config


# Attempt to import Persistent Views
try:
    from cogs.tickets import TicketStarter, CloseTicket
    from cogs.verify import VerifyView
except ImportError:
    TicketStarter, CloseTicket, VerifyView = None, None, None

load_dotenv()

# ── 2. BOT INSTANCE ──────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# ── 3. MODULE REGISTRY (omni_status Removed) ──────────────────────────────────
COGS = [
    'cogs.dashboard', 'cogs.admin', 'cogs.music', 'cogs.fun',
    'cogs.info', 'cogs.economy', 'cogs.giveaways', 'cogs.utilities',
    'cogs.voice_manager', 'cogs.web_bridge', 'cogs.rizz_engine',
    'cogs.voice_features', 'cogs.memes',
    'cogs.verify', 'cogs.autorole', 'cogs.ghostping',
    'cogs.stats', 'cogs.tickets', 'cogs.sentinel', 'cogs.codepilot',
    'cogs.log_relay', 'cogs.welcome', 'cogs.anime', 'cogs.levels', 'cogs.help',
]

# ── 4. STARTUP & SYNC ─────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f'\033[1;32m✅ MINNAL SYSTEM ONLINE:\033[0m {bot.user}')
    
    # Register Persistent Views
    if all([TicketStarter, CloseTicket, VerifyView]):
        bot.add_view(TicketStarter())
        bot.add_view(CloseTicket())
        bot.add_view(VerifyView())

    # Sync Slash Commands
    try:
        synced = await bot.tree.sync()
        print(f'\033[1;34m[SYSTEM]\033[0m Synced {len(synced)} slash commands.')
    except Exception as e:
        print(f'\033[1;31m[ERROR]\033[0m Sync failure: {e}')

# ── 5. MAIN EXECUTION ─────────────────────────────────────────────────────────

async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"\033[1;32m[LOADED]\033[0m {cog}")
            except Exception as e:
                print(f"\033[1;31m[FAILED]\033[0m {cog}: {e}")
        
        TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\033[1;33m[OFFLINE]\033[0m Shutdown complete.")
