# =============================================================================
#  cogs/omni_status.py — THE PROFESSIONAL STATUS ENGINE
#  Target: Sidebar Activity Menu (Mobile Icon + Rotating Status)
# =============================================================================

import discord
from discord.ext import commands, tasks
import random

class OmniStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stream_url = "https://twitch.tv/discord"
        self.rotate_status_menu.start()

    def cog_unload(self):
        self.rotate_status_menu.cancel()

    @tasks.loop(seconds=30)
    async def rotate_status_menu(self):
        """Dedicated loop to update the bot's activity menu every 30 seconds"""
        try:
            # 1. Real-time User & Server Calculation
            total_users = sum(guild.member_count for guild in self.bot.guilds)
            
            # Format numbers (e.g., 1200 -> 1.2K)
            if total_users >= 1000000:
                user_display = f"{total_users / 1000000:.1f}M"
            elif total_users >= 1000:
                user_display = f"{total_users / 1000:.1f}K"
            else:
                user_display = str(total_users)

            # 2. Professional Menu Options
            status_options = [
                {"text": f"MINNAL | {user_display} Users", "type": "streaming"},
                {"text": f"Serving {len(self.bot.guilds)} Servers", "type": "watching"},
                {"text": "Special Grade V2.0", "type": "playing"},
                {"text": "High Fidelity Music", "type": "listening"},
                {"text": "with Lightning Speed", "type": "competing"}
            ]
            
            # Pick a random style and text
            current = random.choice(status_options)
            
            # 3. Rotate Status Color (Online/DND/Idle)
            # This keeps the mobile icon color changing
            status_color = random.choice([
                discord.Status.online, 
                discord.Status.dnd, 
                discord.Status.idle
            ])

            # 4. Construct the Activity Object
            if current["type"] == "streaming":
                activity = discord.Streaming(name=current["text"], url=self.stream_url)
            elif current["type"] == "listening":
                activity = discord.Activity(type=discord.ActivityType.listening, name=current["text"])
            elif current["type"] == "watching":
                activity = discord.Activity(type=discord.ActivityType.watching, name=current["text"])
            elif current["type"] == "competing":
                activity = discord.Activity(type=discord.ActivityType.competing, name=current["text"])
            else: # playing
                activity = discord.Game(name=current["text"])

            # 5. Push the update to Discord
            await self.bot.change_presence(activity=activity, status=status_color)

        except Exception as e:
            print(f"❌ Omni Menu Error: {e}", flush=True)

    @rotate_status_menu.before_loop
    async def before_rotate(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(OmniStatus(bot))
