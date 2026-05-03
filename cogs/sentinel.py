# =============================================================================
#  cogs/sentinel.py — MINNAL Sentinel (Staff-only security log)
#  Logs join/leave events to a PRIVATE staff channel only.
#  Channel is set via data/settings.json → sentinel → log_channel_id
#  Falls back to config.STAFF_LOG_CHANNEL_ID if set, otherwise stays silent.
#  Ticket-channel-creation noise is intentionally removed.
# =============================================================================

import discord
from discord.ext import commands
from datetime import datetime, timezone
import json, os
import config

SETTINGS_FILE = "data/settings.json"


def _log_channel_id() -> int | None:
    """Read sentinel log channel from settings, never from public channels."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            cid = (data.get("sentinel") or {}).get("log_channel_id")
            if cid:
                return int(cid)
    except Exception:
        pass
    # Fallback: only use STAFF_LOG_CHANNEL_ID if explicitly defined
    fallback = getattr(config, "STAFF_LOG_CHANNEL_ID", None)
    return int(fallback) if fallback else None


class Sentinel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        cid = _log_channel_id()
        return guild.get_channel(cid) if cid else None

    # ── Member Join ───────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self._channel(member.guild)
        if not channel:
            return
        embed = discord.Embed(
            title="🛡️ SENTINEL | INBOUND TRAFFIC",
            description=(
                f"**User:** {member.mention} `({member.id})`\n"
                f"**Account Age:** <t:{int(member.created_at.timestamp())}:R>"
            ),
            color=0x2ecc71,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Scanning for threats... Status: Clean")
        await channel.send(embed=embed)

    # ── Member Leave ──────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = self._channel(member.guild)
        if not channel:
            return
        embed = discord.Embed(
            title="🛡️ SENTINEL | DEPARTURE LOG",
            description=(
                f"**User:** `{member.name}`\n"
                f"**ID:** `{member.id}`"
            ),
            color=0xe74c3c,
            timestamp=datetime.now(timezone.utc)
        )
        await channel.send(embed=embed)

    # ── Emergency Lockdown ────────────────────────────────────────────────

    @discord.app_commands.command(name="lockdown", description="🚨 Emergency lockdown for a channel")
    @discord.app_commands.describe(channel="Channel to lock (defaults to current)")
    async def lockdown(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Administrators only.", ephemeral=True)
            return
        target = channel or interaction.channel
        await target.set_permissions(interaction.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="⚠️ CHANNEL LOCKDOWN",
            description=f"{target.mention} has been locked by {interaction.user.mention}.\nOnly Staff may speak.",
            color=0xff4757,
            timestamp=datetime.now(timezone.utc)
        )
        await interaction.response.send_message(embed=embed)

        # Also log to sentinel channel if configured
        log = self._channel(interaction.guild)
        if log and log.id != target.id:
            await log.send(embed=embed)

    @discord.app_commands.command(name="unlockdown", description="🔓 Lift a channel lockdown")
    @discord.app_commands.describe(channel="Channel to unlock (defaults to current)")
    async def unlockdown(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Administrators only.", ephemeral=True)
            return
        target = channel or interaction.channel
        await target.set_permissions(interaction.guild.default_role, send_messages=None)
        embed = discord.Embed(
            title="✅ LOCKDOWN LIFTED",
            description=f"{target.mention} is now open again.",
            color=0x2ecc71,
            timestamp=datetime.now(timezone.utc)
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Sentinel(bot))
