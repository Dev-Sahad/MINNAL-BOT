# =============================================================================
#  cogs/stats.py — MINNAL Growth & System Analytics
# =============================================================================

import discord
from discord.ext import commands
from discord import app_commands
import datetime

class MinnalStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="stats", description="⚡ View lightning-fast server growth analytics")
    @app_commands.describe(member="Optional: View specific user stats")
    async def stats(self, ctx, member: discord.Member = None):
        """Shows analytics about the server or a specific member"""
        guild = ctx.guild
        
        if member:
            # Individual Member Stats
            embed = discord.Embed(
                title=f"👤 User Intel: {member.display_name}",
                color=0x3498db,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
            embed.set_footer(text=f"ID: {member.id}")
            
        else:
            # Global Server Stats
            total = guild.member_count
            bots = sum(1 for m in guild.members if m.bot)
            humans = total - bots
            
            # Text-based progress bar
            bar_length = 15
            human_ratio = int((humans / total) * bar_length) if total > 0 else 0
            bar = "⚡" * human_ratio + "⚪" * (bar_length - human_ratio)

            embed = discord.Embed(
                title=f"📊 {guild.name} | Growth Analytics",
                description="**Real-time population breakdown**",
                color=0xFFD700, # Gold
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Total Members", value=f"**{total}**", inline=True)
            embed.add_field(name="Humans", value=f"`{humans}`", inline=True)
            embed.add_field(name="Bots", value=f"`{bots}`", inline=True)
            embed.add_field(name="Population Mix", value=f"`{bar}`", inline=False)
            
            # Nitro Boost Info
            boosters = guild.premium_subscription_count
            tier = guild.premium_tier
            embed.add_field(name="Boost Level", value=f"Tier {tier} ({boosters} Boosts)", inline=True)
            embed.add_field(name="Channels", value=f"{len(guild.channels)}", inline=True)

            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            embed.set_footer(text="MINNAL Core • Data is Power")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MinnalStats(bot))
