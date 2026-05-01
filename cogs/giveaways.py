# =============================================================================
#  cogs/giveaways.py — Giveaway & Event Management System
#  Features: Giveaways, random winners, event scheduling
# =============================================================================

import discord
from discord import app_commands, ui
from discord.ext import commands
from datetime import datetime, timedelta
import random
import asyncio
from cogs.checks import is_admin


class GiveawayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_giveaways = {}

    # ── /giveaway ─────────────────────────────────────────────────────────────
    @app_commands.command(name="giveaway", description="Start a giveaway (Admin only)")
    @app_commands.describe(
        prize="What you're giving away",
        duration="Duration in minutes",
        winners="Number of winners"
    )
    @is_admin()
    async def slash_giveaway(
        self,
        interaction: discord.Interaction,
        prize: str,
        duration: int,
        winners: int = 1
    ):
        if duration < 1 or duration > 10080:  # Max 1 week
            return await interaction.response.send_message(
                "❌ Duration must be between 1 minute and 1 week (10080 minutes)",
                ephemeral=True
            )
        
        if winners < 1 or winners > 20:
            return await interaction.response.send_message(
                "❌ Number of winners must be between 1 and 20",
                ephemeral=True
            )
        
        end_time = datetime.utcnow() + timedelta(minutes=duration)
        
        embed = discord.Embed(
            title="🎉 GIVEAWAY! 🎉",
            description=f"**Prize:** {prize}\n\nReact with 🎉 to enter!",
            color=discord.Color.gold(),
            timestamp=end_time
        )
        embed.add_field(name="⏰ Ends", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
        embed.add_field(name="🏆 Winners", value=str(winners), inline=True)
        embed.set_footer(text="Good luck!", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🎉")
        
        # Store giveaway data
        self.active_giveaways[message.id] = {
            'prize': prize,
            'winners': winners,
            'end_time': end_time,
            'channel_id': interaction.channel.id
        }
        
        # Wait for giveaway to end
        await asyncio.sleep(duration * 60)
        await self.end_giveaway(message.id)

    async def end_giveaway(self, message_id: int):
        """End a giveaway and pick winners"""
        if message_id not in self.active_giveaways:
            return
        
        giveaway_data = self.active_giveaways[message_id]
        channel = self.bot.get_channel(giveaway_data['channel_id'])
        
        if not channel:
            del self.active_giveaways[message_id]
            return
        
        try:
            message = await channel.fetch_message(message_id)
        except:
            del self.active_giveaways[message_id]
            return
        
        # Get participants
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        if not reaction:
            embed = discord.Embed(
                title="🎉 Giveaway Ended",
                description=f"**Prize:** {giveaway_data['prize']}\n\n❌ No one entered the giveaway!",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await channel.send(embed=embed)
            del self.active_giveaways[message_id]
            return
        
        users = [user async for user in reaction.users() if not user.bot]
        
        if not users:
            embed = discord.Embed(
                title="🎉 Giveaway Ended",
                description=f"**Prize:** {giveaway_data['prize']}\n\n❌ No valid participants!",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await channel.send(embed=embed)
            del self.active_giveaways[message_id]
            return
        
        # Pick winners
        num_winners = min(giveaway_data['winners'], len(users))
        winners = random.sample(users, num_winners)
        
        winner_mentions = ", ".join(winner.mention for winner in winners)
        
        embed = discord.Embed(
            title="🎊 Giveaway Ended! 🎊",
            description=f"**Prize:** {giveaway_data['prize']}\n\n🏆 **Winner{'s' if num_winners > 1 else ''}:** {winner_mentions}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Congratulations!")
        
        await channel.send(f"🎉 {winner_mentions}", embed=embed)
        del self.active_giveaways[message_id]

    # ── /reroll ───────────────────────────────────────────────────────────────
    @app_commands.command(name="reroll", description="Reroll a giveaway winner (Admin only)")
    @app_commands.describe(message_id="ID of the giveaway message")
    @is_admin()
    async def slash_reroll(self, interaction: discord.Interaction, message_id: str):
        try:
            message = await interaction.channel.fetch_message(int(message_id))
        except:
            return await interaction.response.send_message("❌ Message not found!", ephemeral=True)
        
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        if not reaction:
            return await interaction.response.send_message("❌ No giveaway reaction found!", ephemeral=True)
        
        users = [user async for user in reaction.users() if not user.bot]
        
        if not users:
            return await interaction.response.send_message("❌ No participants found!", ephemeral=True)
        
        winner = random.choice(users)
        
        embed = discord.Embed(
            title="🔄 Giveaway Rerolled",
            description=f"🏆 **New Winner:** {winner.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(f"🎉 {winner.mention}", embed=embed)

    # ── /pick ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="pick", description="Pick random member(s) from the server")
    @app_commands.describe(count="Number of members to pick")
    async def slash_pick(self, interaction: discord.Interaction, count: int = 1):
        if count < 1 or count > 10:
            return await interaction.response.send_message(
                "❌ Count must be between 1 and 10",
                ephemeral=True
            )
        
        members = [m for m in interaction.guild.members if not m.bot]
        
        if count > len(members):
            return await interaction.response.send_message(
                f"❌ Not enough members! Server has {len(members)} non-bot members.",
                ephemeral=True
            )
        
        picked = random.sample(members, count)
        
        embed = discord.Embed(
            title="🎲 Random Pick",
            description="\n".join(f"**{i+1}.** {member.mention}" for i, member in enumerate(picked)),
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Picked by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(GiveawayCog(bot))
