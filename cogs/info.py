# =============================================================================
#  cogs/info.py — /info command
#  Shows a full command directory + live bot stats + developer credit.
# =============================================================================

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import config


class InfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="info", description="Display bot information and all available commands")
    async def slash_info(self, interaction: discord.Interaction):
        guild   = interaction.guild
        current = config.now_playing.get(guild.id if guild else 0)

        desc = (
            "A feature-rich Discord bot for **server management**, **announcements**, and **music** — "
            "all powered by slash commands.\n"
        )
        if current:
            desc += f"\n🎵 **Currently playing:** [{current['title']}]({current['webpage_url']})\n"

        embed = discord.Embed(
            title="🤖 MINNAL Bot",
            description=desc,
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="🔐 Admin Commands",
            value=(
                "`/send` — Send a message to any channel\n"
                "`/embed` — Send a rich embed to a channel\n"
                "`/announce` — Post a styled announcement\n"
                "`/gameupdate` — Post a manual game update\n"
                "`/post` — Send a fully styled colour post\n"
                "`/welcome` — Set the welcome channel\n"
                "`/leavechannel` — Set the goodbye channel\n"
                "`/gamechannel` — Set the game updates channel\n"
                "`/setwelcomeimage` — Set/clear the welcome image\n"
                "`/setleaveimage` — Set/clear the goodbye image\n"
                "`/setmusicchannel` — Lock music to a channel\n"
                "`/admin` — View admin dashboard & server stats\n"
                "`/panel` — Open the interactive settings panel"
            ),
            inline=False
        )
        embed.add_field(
            name="🎵 Music Commands",
            value=(
                "`/play` — Play a song or add to queue\n"
                "`/pause` — Pause playback\n"
                "`/resume` — Resume playback\n"
                "`/skip` — Skip the current song\n"
                "`/stop` — Stop music and clear the queue\n"
                "`/queue` — View the music queue\n"
                "`/nowplaying` — Show the current song\n"
                "`/volume` — Set volume (1–100)\n"
                "`/join` — Join your voice channel\n"
                "`/leave` — Disconnect from voice"
            ),
            inline=False
        )
        embed.add_field(
            name="🎮 Fun & Utility Commands",
            value=(
                "`/roll` — Roll a dice (e.g. `1d6`, `2d20`)\n"
                "`/8ball` — Ask the magic 8-ball a question\n"
                "`/remindme` — Set a reminder via DM (e.g. `10m`, `2h`)\n"
                "`/clean` — Delete messages in a channel *(Admin)*"
            ),
            inline=False
        )
        embed.add_field(
            name="📢 Public Commands",
            value=(
                "`/poll` — Create a reaction poll (up to 5 options)\n"
                "`/info` — Show this info panel"
            ),
            inline=False
        )
        embed.add_field(
            name="✨ Auto Features",
            value=(
                "• Welcome & goodbye messages when members join/leave\n"
                "• Daily game update at 9:00 AM\n"
                "• Dynamic music status (shows current song)"
            ),
            inline=False
        )

        total_queued = sum(len(q) for q in config.music_queues.values())
        embed.add_field(name="🌐 Servers",  value=str(len(self.bot.guilds)),            inline=True)
        embed.add_field(name="📶 Latency",  value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="🎶 Queue",    value=f"{total_queued} tracks",              inline=True)

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Developer: {config.DEVELOPER}",
            icon_url=self.bot.user.display_avatar.url
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(InfoCog(bot))
