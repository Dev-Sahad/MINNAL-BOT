# =============================================================================
#  cogs/economy.py — Economy & Leveling System
#  Features: XP, levels, virtual currency, daily rewards, leaderboards
# =============================================================================

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os
import random
from typing import Optional


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_file = 'data/economy.json'
        self.ensure_data_file()
        self.data = self.load_data()

    def ensure_data_file(self):
        """Create data directory and file if they don't exist"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({}, f)

    def load_data(self):
        """Load economy data from file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_data(self):
        """Save economy data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_user_data(self, user_id: str):
        """Get or create user data"""
        if user_id not in self.data:
            self.data[user_id] = {
                'balance': 0,
                'xp': 0,
                'level': 1,
                'messages': 0,
                'last_daily': None,
                'last_weekly': None,
                'inventory': []
            }
            self.save_data()
        return self.data[user_id]

    def calculate_level(self, xp: int) -> int:
        """Calculate level from XP"""
        # Level formula: level = sqrt(xp / 100)
        return int((xp / 100) ** 0.5) + 1

    def xp_for_next_level(self, level: int) -> int:
        """Calculate XP needed for next level"""
        return (level ** 2) * 100

    # ── Message XP System ─────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Award XP for messages"""
        if message.author.bot:
            return
        
        user_id = str(message.author.id)
        user_data = self.get_user_data(user_id)
        
        # Award random XP (5-15 per message)
        xp_gain = random.randint(5, 15)
        old_level = user_data['level']
        
        user_data['xp'] += xp_gain
        user_data['messages'] += 1
        user_data['level'] = self.calculate_level(user_data['xp'])
        
        # Level up notification
        if user_data['level'] > old_level:
            reward = user_data['level'] * 100
            user_data['balance'] += reward
            
            embed = discord.Embed(
                title="🎉 LEVEL UP!",
                description=f"{message.author.mention} reached **Level {user_data['level']}**!",
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="💰 Reward", value=f"+{reward} coins", inline=True)
            embed.add_field(name="📊 Total XP", value=f"{user_data['xp']:,}", inline=True)
            embed.set_thumbnail(url=message.author.display_avatar.url)
            
            await message.channel.send(embed=embed)
        
        self.save_data()

    # ── /balance ──────────────────────────────────────────────────────────────
    @app_commands.command(name="balance", description="Check your or someone's balance and stats")
    @app_commands.describe(user="User to check (optional)")
    async def slash_balance(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target = user or interaction.user
        user_data = self.get_user_data(str(target.id))
        
        next_level_xp = self.xp_for_next_level(user_data['level'])
        xp_progress = user_data['xp'] - self.xp_for_next_level(user_data['level'] - 1)
        xp_needed = next_level_xp - self.xp_for_next_level(user_data['level'] - 1)
        progress_percent = int((xp_progress / xp_needed) * 100)
        
        embed = discord.Embed(
            title=f"💰 {target.name}'s Profile",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="💵 Balance", value=f"**{user_data['balance']:,}** coins", inline=True)
        embed.add_field(name="⭐ Level", value=f"**{user_data['level']}**", inline=True)
        embed.add_field(name="📈 XP", value=f"**{user_data['xp']:,}**", inline=True)
        embed.add_field(
            name="📊 Progress to Next Level",
            value=f"{'█' * (progress_percent // 10)}{'░' * (10 - progress_percent // 10)} {progress_percent}%\n{xp_progress:,}/{xp_needed:,} XP",
            inline=False
        )
        embed.add_field(name="💬 Messages", value=f"{user_data['messages']:,}", inline=True)
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

    # ── /daily ────────────────────────────────────────────────────────────────
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def slash_daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_data = self.get_user_data(user_id)
        
        now = datetime.utcnow()
        last_daily = datetime.fromisoformat(user_data['last_daily']) if user_data['last_daily'] else None
        
        if last_daily and (now - last_daily).total_seconds() < 86400:  # 24 hours
            time_left = timedelta(seconds=86400 - (now - last_daily).total_seconds())
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            
            embed = discord.Embed(
                title="⏰ Daily Reward Not Ready",
                description=f"You can claim your next daily reward in **{hours}h {minutes}m**",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Award daily reward
        base_reward = 500
        level_bonus = user_data['level'] * 50
        total_reward = base_reward + level_bonus
        
        user_data['balance'] += total_reward
        user_data['last_daily'] = now.isoformat()
        self.save_data()
        
        embed = discord.Embed(
            title="✅ Daily Reward Claimed!",
            description=f"You received **{total_reward:,} coins**!",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="💰 New Balance", value=f"{user_data['balance']:,} coins", inline=True)
        embed.add_field(name="🎁 Bonus", value=f"+{level_bonus} (Level {user_data['level']})", inline=True)
        embed.set_footer(text="Come back in 24 hours!")
        
        await interaction.response.send_message(embed=embed)

    # ── /weekly ───────────────────────────────────────────────────────────────
    @app_commands.command(name="weekly", description="Claim your weekly reward")
    async def slash_weekly(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_data = self.get_user_data(user_id)
        
        now = datetime.utcnow()
        last_weekly = datetime.fromisoformat(user_data['last_weekly']) if user_data['last_weekly'] else None
        
        if last_weekly and (now - last_weekly).total_seconds() < 604800:  # 7 days
            time_left = timedelta(seconds=604800 - (now - last_weekly).total_seconds())
            days = int(time_left.total_seconds() // 86400)
            hours = int((time_left.total_seconds() % 86400) // 3600)
            
            embed = discord.Embed(
                title="⏰ Weekly Reward Not Ready",
                description=f"You can claim your next weekly reward in **{days}d {hours}h**",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Award weekly reward
        base_reward = 5000
        level_bonus = user_data['level'] * 500
        total_reward = base_reward + level_bonus
        
        user_data['balance'] += total_reward
        user_data['last_weekly'] = now.isoformat()
        self.save_data()
        
        embed = discord.Embed(
            title="🎁 Weekly Reward Claimed!",
            description=f"You received **{total_reward:,} coins**!",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="💰 New Balance", value=f"{user_data['balance']:,} coins", inline=True)
        embed.add_field(name="🎁 Bonus", value=f"+{level_bonus} (Level {user_data['level']})", inline=True)
        embed.set_footer(text="Come back in 7 days!")
        
        await interaction.response.send_message(embed=embed)

    # ── /leaderboard ──────────────────────────────────────────────────────────
    @app_commands.command(name="leaderboard", description="View server leaderboard")
    @app_commands.describe(category="What to rank by")
    @app_commands.choices(category=[
        app_commands.Choice(name="💰 Balance", value="balance"),
        app_commands.Choice(name="⭐ Level", value="level"),
        app_commands.Choice(name="💬 Messages", value="messages")
    ])
    async def slash_leaderboard(self, interaction: discord.Interaction, category: str = "level"):
        # Sort users by category
        sorted_users = sorted(
            self.data.items(),
            key=lambda x: x[1].get(category, 0),
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title=f"🏆 Leaderboard - {category.title()}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, (user_id, data) in enumerate(sorted_users):
            try:
                user = await self.bot.fetch_user(int(user_id))
                medal = medals[idx] if idx < 3 else f"**{idx + 1}.**"
                
                if category == "balance":
                    value = f"{data['balance']:,} coins"
                elif category == "level":
                    value = f"Level {data['level']} ({data['xp']:,} XP)"
                else:
                    value = f"{data['messages']:,} messages"
                
                embed.add_field(
                    name=f"{medal} {user.name}",
                    value=value,
                    inline=False
                )
            except:
                continue
        
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)

    # ── /give ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="give", description="Give coins to another user")
    @app_commands.describe(user="User to give coins to", amount="Amount of coins")
    async def slash_give(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if user.bot:
            return await interaction.response.send_message("❌ You can't give coins to bots!", ephemeral=True)
        
        if user.id == interaction.user.id:
            return await interaction.response.send_message("❌ You can't give coins to yourself!", ephemeral=True)
        
        if amount <= 0:
            return await interaction.response.send_message("❌ Amount must be positive!", ephemeral=True)
        
        giver_data = self.get_user_data(str(interaction.user.id))
        receiver_data = self.get_user_data(str(user.id))
        
        if giver_data['balance'] < amount:
            return await interaction.response.send_message(
                f"❌ You don't have enough coins! Your balance: {giver_data['balance']:,}",
                ephemeral=True
            )
        
        # Transfer coins
        giver_data['balance'] -= amount
        receiver_data['balance'] += amount
        self.save_data()
        
        embed = discord.Embed(
            title="💸 Transfer Successful",
            description=f"{interaction.user.mention} gave **{amount:,} coins** to {user.mention}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name=f"{interaction.user.name}'s Balance", value=f"{giver_data['balance']:,} coins", inline=True)
        embed.add_field(name=f"{user.name}'s Balance", value=f"{receiver_data['balance']:,} coins", inline=True)
        
        await interaction.response.send_message(embed=embed)

    # ── /coinflip ─────────────────────────────────────────────────────────────
    @app_commands.command(name="coinflip", description="Flip a coin and bet coins")
    @app_commands.describe(bet="Amount to bet", choice="Heads or Tails")
    @app_commands.choices(choice=[
        app_commands.Choice(name="🪙 Heads", value="heads"),
        app_commands.Choice(name="🪙 Tails", value="tails")
    ])
    async def slash_coinflip(self, interaction: discord.Interaction, bet: int, choice: str):
        user_data = self.get_user_data(str(interaction.user.id))
        
        if bet <= 0:
            return await interaction.response.send_message("❌ Bet must be positive!", ephemeral=True)
        
        if user_data['balance'] < bet:
            return await interaction.response.send_message(
                f"❌ Not enough coins! Your balance: {user_data['balance']:,}",
                ephemeral=True
            )
        
        # Flip coin
        result = random.choice(["heads", "tails"])
        won = result == choice
        
        if won:
            user_data['balance'] += bet
            color = discord.Color.green()
            title = "🎉 You Won!"
            description = f"The coin landed on **{result.title()}**!\nYou won **{bet:,} coins**!"
        else:
            user_data['balance'] -= bet
            color = discord.Color.red()
            title = "😔 You Lost"
            description = f"The coin landed on **{result.title()}**...\nYou lost **{bet:,} coins**."
        
        self.save_data()
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="💰 New Balance", value=f"{user_data['balance']:,} coins", inline=True)
        embed.set_footer(text=f"You chose {choice.title()}")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
