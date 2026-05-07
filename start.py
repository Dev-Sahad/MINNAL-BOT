import os
import asyncio
import time
import discord_bot

# ── MAIN EXECUTION ────────────────────────────────────────────────────────────

async def run_bot():
    """Start the Discord bot"""
    print('🤖 Starting Discord bot...', flush=True)
    await discord_bot.main()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n  [OFFLINE]  Shutdown complete.\n")