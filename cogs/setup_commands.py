# =============================================================================
#  cogs/setup_commands.py — Server Setup Commands
# =============================================================================

import discord
from discord.ext import commands
from discord import app_commands
import json
import os


class SetupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/settings.json"

    def load_config(self):
        """Load settings.json"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_config(self, data):
        """Save settings.json"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    @app_commands.command(name="setmusic_channel", description="🎵 Set music channel")
    @app_commands.describe(channel="Music channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setmusic_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the music channel"""
        
        config = self.load_config()
        
        if "music" not in config:
            config["music"] = {}
        
        config["music"]["channel_id"] = str(channel.id)
        self.save_config(config)
        
        embed = discord.Embed(
            title="✅ Music Channel Set",
            description=f"Music commands now work only in {channel.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"✅ Music channel set to {channel.name} in {interaction.guild.name}", flush=True)


async def setup(bot):
    await bot.add_cog(SetupCommands(bot))