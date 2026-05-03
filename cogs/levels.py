# =============================================================================
#  cogs/levels.py — XP / Level System
#  - XP per message (60s cooldown per user to prevent spam)
#  - Level-up announcements
#  - Role rewards at configurable milestones
#  - /rank, /leaderboard, /setlevel, /addxp commands
# =============================================================================

import discord
from discord.ext import commands
import json
import os
import math
import random
import asyncio
from datetime import datetime, timezone

XP_FILE   = "data/xp.json"
CONF_FILE = "data/settings.json"

XP_MIN      = 15   # min XP per message
XP_MAX      = 25   # max XP per message
XP_COOLDOWN = 60   # seconds between XP grants per user

# ── Level formula ──────────────────────────────────────────────────────────
# XP needed to reach a level:  5n² + 50n + 100
def xp_for_level(level: int) -> int:
    return 5 * (level ** 2) + 50 * level + 100

def total_xp_for_level(level: int) -> int:
    return sum(xp_for_level(l) for l in range(level))

def level_from_xp(xp: int) -> int:
    level = 0
    while xp >= total_xp_for_level(level + 1):
        level += 1
    return level

def xp_progress(xp: int):
    level      = level_from_xp(xp)
    total_now  = total_xp_for_level(level)
    total_next = total_xp_for_level(level + 1)
    current    = xp - total_now
    needed     = total_next - total_now
    return level, current, needed

def make_bar(current: int, needed: int, length: int = 14) -> str:
    filled = round((current / needed) * length) if needed else length
    filled = max(0, min(filled, length))
    return "█" * filled + "░" * (length - filled)

# ── Default role rewards: { level: role_id } ──────────────────────────────
DEFAULT_ROLE_REWARDS: dict[int, int] = {
    # Fill these in via /setreward or the settings file
}


def _load_xp() -> dict:
    try:
        if os.path.exists(XP_FILE):
            with open(XP_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_xp(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(XP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _load_settings() -> dict:
    try:
        if os.path.exists(CONF_FILE):
            with open(CONF_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_settings(data: dict):
    with open(CONF_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _level_config(settings: dict) -> dict:
    return settings.get("levels", {})


class Levels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot      = bot
        self.cooldown: dict[int, float] = {}
        print("🏆 Levels cog loaded!", flush=True)

    # ── XP grant on message ────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        uid  = str(message.author.id)
        now  = asyncio.get_event_loop().time()
        last = self.cooldown.get(message.author.id, 0)

        if now - last < XP_COOLDOWN:
            return
        self.cooldown[message.author.id] = now

        xp_data = _load_xp()
        guild_id = str(message.guild.id)

        if guild_id not in xp_data:
            xp_data[guild_id] = {}

        user = xp_data[guild_id].get(uid, {"xp": 0, "level": 0, "messages": 0})
        old_level = user["level"]

        gained       = random.randint(XP_MIN, XP_MAX)
        user["xp"]  += gained
        user["messages"] = user.get("messages", 0) + 1
        new_level    = level_from_xp(user["xp"])
        user["level"] = new_level

        xp_data[guild_id][uid] = user
        _save_xp(xp_data)

        if new_level > old_level:
            await self._on_level_up(message, new_level)

    # ── Level-up handler ───────────────────────────────────────────────────

    async def _on_level_up(self, message: discord.Message, new_level: int):
        settings   = _load_settings()
        lvl_cfg    = _level_config(settings)
        channel_id = lvl_cfg.get("levelup_channel_id")

        channel = (
            self.bot.get_channel(int(channel_id))
            if channel_id else message.channel
        )

        if channel:
            embed = discord.Embed(
                title="⚡ Level Up!",
                description=(
                    f"🎉 {message.author.mention} just reached **Level {new_level}**!\n"
                    f"Keep chatting to climb higher! 🚀"
                ),
                color=0x7c5cfc,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text=f"{message.guild.name} · XP System")
            await channel.send(embed=embed)

        # Apply role reward if configured
        role_rewards: dict = lvl_cfg.get("role_rewards", {})
        role_id = role_rewards.get(str(new_level))
        if role_id:
            role = message.guild.get_role(int(role_id))
            if role:
                try:
                    await message.author.add_roles(role, reason=f"Level {new_level} reward")
                    print(f"🏆 Gave role {role.name} to {message.author} for level {new_level}", flush=True)
                except discord.Forbidden:
                    print(f"🏆 [Levels] Missing permission to assign role {role.name}", flush=True)

    # ── /rank ──────────────────────────────────────────────────────────────

    @discord.app_commands.command(name="rank", description="See your XP rank card")
    @discord.app_commands.describe(member="Member to check (leave empty for yourself)")
    async def rank_cmd(self, interaction: discord.Interaction, member: discord.Member = None):
        target   = member or interaction.user
        xp_data  = _load_xp()
        guild_id = str(interaction.guild_id)
        uid      = str(target.id)

        user = xp_data.get(guild_id, {}).get(uid, {"xp": 0, "level": 0, "messages": 0})
        xp       = user["xp"]
        level, current, needed = xp_progress(xp)
        bar      = make_bar(current, needed)
        messages = user.get("messages", 0)

        # Calculate server rank
        guild_data = xp_data.get(guild_id, {})
        sorted_users = sorted(guild_data.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
        rank = next((i + 1 for i, (u, _) in enumerate(sorted_users) if u == uid), "?")

        pct = round((current / needed) * 100) if needed else 100

        embed = discord.Embed(
            title=f"⚡ {target.display_name}'s Rank",
            color=0x7c5cfc
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(
            name="🏅 Server Rank",
            value=f"**#{rank}**",
            inline=True
        )
        embed.add_field(
            name="⭐ Level",
            value=f"**{level}**",
            inline=True
        )
        embed.add_field(
            name="✉️ Messages",
            value=f"**{messages:,}**",
            inline=True
        )
        embed.add_field(
            name=f"📊 XP Progress  `{current:,} / {needed:,}` ({pct}%)",
            value=f"`[{bar}]`",
            inline=False
        )
        embed.add_field(
            name="💠 Total XP",
            value=f"**{xp:,}**",
            inline=True
        )
        embed.add_field(
            name="🎯 Next Level",
            value=f"**{needed - current:,} XP** to go",
            inline=True
        )
        embed.set_footer(text=f"{interaction.guild.name} · XP System")
        await interaction.response.send_message(embed=embed)

    # ── /leaderboard ───────────────────────────────────────────────────────

    @discord.app_commands.command(name="leaderboard", description="Top 10 most active members by XP")
    async def leaderboard_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer()
        xp_data  = _load_xp()
        guild_id = str(interaction.guild_id)
        guild_data = xp_data.get(guild_id, {})

        if not guild_data:
            await interaction.followup.send("Nobody has earned any XP yet. Start chatting! 💬", ephemeral=True)
            return

        sorted_users = sorted(guild_data.items(), key=lambda x: x[1].get("xp", 0), reverse=True)[:10]

        medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        lines  = []
        for i, (uid, data) in enumerate(sorted_users):
            member = interaction.guild.get_member(int(uid))
            name   = member.display_name if member else f"User ({uid[:6]}…)"
            xp     = data.get("xp", 0)
            level  = data.get("level", 0)
            lines.append(f"{medals[i]} **{name}**  ·  Level **{level}**  ·  `{xp:,} XP`")

        embed = discord.Embed(
            title=f"🏆 {interaction.guild.name} — XP Leaderboard",
            description="\n".join(lines),
            color=0xf9c74f,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="Earn XP by chatting · Top 10 shown")
        await interaction.followup.send(embed=embed)

    # ── /addxp (admin) ─────────────────────────────────────────────────────

    @discord.app_commands.command(name="addxp", description="[Admin] Add XP to a member")
    @discord.app_commands.describe(member="Target member", amount="Amount of XP to add")
    @discord.app_commands.default_permissions(administrator=True)
    async def addxp_cmd(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.", ephemeral=True)
            return

        xp_data  = _load_xp()
        guild_id = str(interaction.guild_id)
        uid      = str(member.id)

        if guild_id not in xp_data:
            xp_data[guild_id] = {}
        user = xp_data[guild_id].get(uid, {"xp": 0, "level": 0, "messages": 0})
        old_level    = user["level"]
        user["xp"]  += amount
        user["level"] = level_from_xp(user["xp"])
        xp_data[guild_id][uid] = user
        _save_xp(xp_data)

        embed = discord.Embed(
            description=f"✅ Added **{amount:,} XP** to {member.mention}\n"
                        f"They are now Level **{user['level']}** with **{user['xp']:,} XP** total.",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed)

        if user["level"] > old_level:
            class FakeMsgCtx:
                author = member
                channel = interaction.channel
                guild   = interaction.guild
            await self._on_level_up(FakeMsgCtx(), user["level"])

    # ── /setlevel (admin) ──────────────────────────────────────────────────

    @discord.app_commands.command(name="setlevel", description="[Admin] Set a member's level directly")
    @discord.app_commands.describe(member="Target member", level="Level to set")
    @discord.app_commands.default_permissions(administrator=True)
    async def setlevel_cmd(self, interaction: discord.Interaction, member: discord.Member, level: int):
        if level < 0:
            await interaction.response.send_message("❌ Level must be 0 or higher.", ephemeral=True)
            return

        xp_data  = _load_xp()
        guild_id = str(interaction.guild_id)
        uid      = str(member.id)

        if guild_id not in xp_data:
            xp_data[guild_id] = {}

        new_xp = total_xp_for_level(level)
        xp_data[guild_id][uid] = {
            "xp":      new_xp,
            "level":   level,
            "messages": xp_data[guild_id].get(uid, {}).get("messages", 0)
        }
        _save_xp(xp_data)

        embed = discord.Embed(
            description=f"✅ Set {member.mention}'s level to **{level}** (`{new_xp:,} XP`)",
            color=0x7c5cfc
        )
        await interaction.response.send_message(embed=embed)

    # ── /resetxp (admin) ───────────────────────────────────────────────────

    @discord.app_commands.command(name="resetxp", description="[Admin] Reset a member's XP to zero")
    @discord.app_commands.describe(member="Member to reset")
    @discord.app_commands.default_permissions(administrator=True)
    async def resetxp_cmd(self, interaction: discord.Interaction, member: discord.Member):
        xp_data  = _load_xp()
        guild_id = str(interaction.guild_id)
        uid      = str(member.id)
        xp_data.setdefault(guild_id, {}).pop(uid, None)
        _save_xp(xp_data)
        await interaction.response.send_message(f"✅ Reset **{member.display_name}**'s XP.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Levels(bot))
