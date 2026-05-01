import discord
from discord.ext import commands
from datetime import datetime
import config

class Sentinel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_log_channel(self, guild):
        # Redirects all security logs to your game update or a dedicated staff channel
        return guild.get_channel(config.GAME_UPDATE_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.get_log_channel(member.guild)
        if not channel: return

        embed = discord.Embed(
            title="` 🛡️ ` **SENTINEL | INBOUND TRAFFIC**",
            description=f"**User:** {member.mention} ({member.id})\n**Account Age:** <t:{int(member.created_at.timestamp())}:R>",
            color=0x2ecc71,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Scanning for threats... Status: Clean")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.get_log_channel(member.guild)
        if not channel: return

        embed = discord.Embed(
            title="` 🛡️ ` **SENTINEL | DEPARTURE LOG**",
            description=f"**User:** {member.name}#{member.discriminator}\n**ID:** {member.id}",
            color=0xe74c3c,
            timestamp=datetime.utcnow()
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        # Detects when a new ticket thread/channel is created
        log_channel = self.get_log_channel(channel.guild)
        if not log_channel: return

        embed = discord.Embed(
            title="` 🎫 ` **SENTINEL | TICKET INITIALIZED**",
            description=f"**Channel:** {channel.mention}\n**Category:** {channel.category}",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    @commands.hybrid_command(name="lockdown", description="Emergency server lockdown")
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx):
        """Prevents @everyone from sending messages in the current channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="` ⚠️ ` **CHANNEL LOCKDOWN**",
            description="Access restricted by MINNAL Sentinel. Only Staff may speak.",
            color=0xff4757
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Sentinel(bot))
