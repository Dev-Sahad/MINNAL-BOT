# =============================================================================
#  cogs/bot_control.py — MINNAL Admin Control Center
#  Gives admins total control over the bot:
#    • Global bot lock   (/admin lock / unlock)
#    • Feature toggles   (/admin feature enable/disable)
#    • Command restrict  (/admin restrict / unrestrict)
#    • Audit log         (every admin action → designated channel)
#    • Announcements     (/admin announce)
#    • Full status dash  (/admin status)
# =============================================================================

import discord
from discord.ext import commands
from discord import app_commands
import json, os
from datetime import datetime, timezone
import config
import logger as log

CONTROL_FILE = "data/bot_control.json"

# ── Feature registry (name → friendly label) ─────────────────────────────────
FEATURES = {
    "ai_chat":   "Claude AI Chat",
    "anime":     "Anime system & daily posts",
    "levels":    "XP & level system",
    "memes":     "Auto meme poster",
    "music":     "Voice & music player",
    "welcome":   "Welcome & goodbye system",
    "economy":   "Virtual economy & coins",
    "giveaways": "Giveaway system",
    "fun":       "Fun commands",
    "watchlist": "Anime watchlist",
    "log_relay": "Railway log relay",
    "tickets":   "Ticket system",
    "stats":     "Server statistics",
}

ACCENT   = 0x2f3136
LOCK_CLR = 0xff4757
OK_CLR   = 0x2ed573
WARN_CLR = 0xffa502


# ── State helpers ─────────────────────────────────────────────────────────────

def _load() -> dict:
    try:
        if os.path.exists(CONTROL_FILE):
            with open(CONTROL_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {
        "locked": False,
        "lock_reason": "",
        "locked_by_id": None,
        "locked_by_name": "",
        "locked_at": None,
        "audit_channel_id": None,
        "disabled_features": [],
        "command_restrictions": {},   # command_name → role_id
    }


def _save(state: dict):
    os.makedirs("data", exist_ok=True)
    with open(CONTROL_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ── Public accessors used by discord_bot.py global check ─────────────────────

def is_bot_locked() -> bool:
    return _load().get("locked", False)


def get_lock_reason() -> str:
    return _load().get("lock_reason") or "Bot is under admin maintenance."


def get_disabled_features() -> list:
    return _load().get("disabled_features", [])


def get_command_restrictions() -> dict:
    return _load().get("command_restrictions", {})


# ── Admin check helper ────────────────────────────────────────────────────────

def _is_admin(interaction: discord.Interaction) -> bool:
    if interaction.user.id in config.DEVELOPER_IDS:
        return True
    if interaction.guild and interaction.guild.owner_id == interaction.user.id:
        return True
    member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
    return bool(member and member.guild_permissions.administrator)


# ── Audit log helper ──────────────────────────────────────────────────────────

async def _audit(bot: commands.Bot, action: str, detail: str, actor: discord.User, color: int = ACCENT):
    state = _load()
    cid = state.get("audit_channel_id")
    if not cid:
        return
    channel = bot.get_channel(int(cid))
    if not channel:
        return
    embed = discord.Embed(
        title=f"🛡️ Admin Action  —  {action}",
        description=detail,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_author(name=str(actor), icon_url=actor.display_avatar.url)
    embed.set_footer(text="MINNAL Admin Audit Log")
    try:
        await channel.send(embed=embed)
    except Exception:
        pass


# ── Feature status emoji ──────────────────────────────────────────────────────

def _feat_icon(name: str, disabled: list) -> str:
    return "🔴" if name in disabled else "🟢"


# ── The Cog ───────────────────────────────────────────────────────────────────

class BotControl(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    admin = app_commands.Group(
        name="admin",
        description="🛡️ MINNAL Admin Control — lock, features, restrictions, audit log"
    )

    # ── /admin status ─────────────────────────────────────────────────────

    @admin.command(name="status", description="Full bot control dashboard")
    @app_commands.check(lambda i: _is_admin(i))
    async def status(self, interaction: discord.Interaction):
        state    = _load()
        disabled = state.get("disabled_features", [])
        locked   = state.get("locked", False)
        restrs   = state.get("command_restrictions", {})
        audit_id = state.get("audit_channel_id")

        lock_line = (
            f"🔒 **LOCKED** — *{state.get('lock_reason') or 'No reason given'}*\n"
            f"By {state.get('locked_by_name', '?')} at `{state.get('locked_at', '?')}`"
            if locked else "🔓 **Unlocked** — all members can use commands"
        )

        feat_lines = "\n".join(
            f"{_feat_icon(n, disabled)} `{n:<14}` {label}"
            for n, label in FEATURES.items()
        )

        restr_lines = (
            "\n".join(f"• `/{cmd}` → <@&{rid}>" for cmd, rid in restrs.items())
            if restrs else "*None configured*"
        )

        embed = discord.Embed(
            title="🛡️ MINNAL Admin Control Dashboard",
            color=LOCK_CLR if locked else OK_CLR,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Bot Lock", value=lock_line, inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Feature States", value=feat_lines, inline=False)
        embed.add_field(name="Command Restrictions", value=restr_lines, inline=False)
        embed.add_field(
            name="Audit Log Channel",
            value=f"<#{audit_id}>" if audit_id else "*Not configured*  —  use `/admin setlog`",
            inline=False
        )
        embed.set_footer(text=f"MINNAL  ·  {len(restrs)} restrictions  ·  {len(disabled)} features disabled")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /admin lock ───────────────────────────────────────────────────────

    @admin.command(name="lock", description="Lock the bot — only admins can use commands")
    @app_commands.describe(reason="Why the bot is being locked")
    @app_commands.check(lambda i: _is_admin(i))
    async def lock(self, interaction: discord.Interaction, reason: str = "Under admin maintenance"):
        state = _load()
        if state.get("locked"):
            await interaction.response.send_message(
                "⚠️ Bot is already locked. Use `/admin unlock` first.", ephemeral=True
            )
            return
        state["locked"]          = True
        state["lock_reason"]     = reason
        state["locked_by_id"]    = interaction.user.id
        state["locked_by_name"]  = str(interaction.user)
        state["locked_at"]       = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        _save(state)

        embed = discord.Embed(
            title="🔒 Bot Locked",
            description=f"**Reason:** {reason}\n\nOnly administrators can use commands now.",
            color=LOCK_CLR
        )
        embed.set_footer(text=f"Locked by {interaction.user}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await _audit(self.bot, "Bot Locked", f"**Reason:** {reason}", interaction.user, LOCK_CLR)
        log.warning("admin", f"Bot LOCKED by {interaction.user} — {reason}")

    # ── /admin unlock ─────────────────────────────────────────────────────

    @admin.command(name="unlock", description="Unlock the bot — all members can use commands again")
    @app_commands.check(lambda i: _is_admin(i))
    async def unlock(self, interaction: discord.Interaction):
        state = _load()
        if not state.get("locked"):
            await interaction.response.send_message("⚠️ Bot is not currently locked.", ephemeral=True)
            return
        state["locked"]         = False
        state["lock_reason"]    = ""
        state["locked_by_id"]   = None
        state["locked_by_name"] = ""
        state["locked_at"]      = None
        _save(state)

        embed = discord.Embed(
            title="🔓 Bot Unlocked",
            description="All members can use commands again.",
            color=OK_CLR
        )
        embed.set_footer(text=f"Unlocked by {interaction.user}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await _audit(self.bot, "Bot Unlocked", "Bot is now accessible to all members.", interaction.user, OK_CLR)
        log.event("admin", f"Bot UNLOCKED by {interaction.user}")

    # ── /admin feature ────────────────────────────────────────────────────

    @admin.command(name="feature", description="Enable or disable a bot feature")
    @app_commands.describe(
        feature="Which feature to toggle",
        action="Enable or disable"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="✅ Enable",  value="enable"),
        app_commands.Choice(name="🔴 Disable", value="disable"),
    ])
    @app_commands.check(lambda i: _is_admin(i))
    async def feature(self, interaction: discord.Interaction, feature: str, action: str):
        if feature not in FEATURES:
            names = ", ".join(f"`{n}`" for n in FEATURES)
            await interaction.response.send_message(
                f"❌ Unknown feature `{feature}`.\nAvailable: {names}", ephemeral=True
            )
            return
        state    = _load()
        disabled = state.setdefault("disabled_features", [])
        label    = FEATURES[feature]

        if action == "disable":
            if feature in disabled:
                await interaction.response.send_message(f"⚠️ `{feature}` is already disabled.", ephemeral=True)
                return
            disabled.append(feature)
            msg   = f"🔴 **{label}** has been **disabled**."
            color = LOCK_CLR
        else:
            if feature not in disabled:
                await interaction.response.send_message(f"⚠️ `{feature}` is already enabled.", ephemeral=True)
                return
            disabled.remove(feature)
            msg   = f"🟢 **{label}** has been **enabled**."
            color = OK_CLR

        _save(state)
        embed = discord.Embed(description=msg, color=color)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await _audit(self.bot, f"Feature {action.title()}d", msg, interaction.user, color)
        log.event("admin", f"Feature '{feature}' → {action}d by {interaction.user}")

    # ── /admin restrict ───────────────────────────────────────────────────

    @admin.command(name="restrict", description="Restrict a slash command to a specific role")
    @app_commands.describe(
        command_name="Command name (e.g. anime, rizz_check, help)",
        role="Only members with this role can use the command"
    )
    @app_commands.check(lambda i: _is_admin(i))
    async def restrict(self, interaction: discord.Interaction, command_name: str, role: discord.Role):
        state = _load()
        state.setdefault("command_restrictions", {})[command_name] = str(role.id)
        _save(state)
        msg = f"🔐 `/{command_name}` is now restricted to {role.mention}."
        await interaction.response.send_message(msg, ephemeral=True)
        await _audit(self.bot, "Command Restricted", msg, interaction.user, WARN_CLR)
        log.event("admin", f"/{command_name} restricted to @{role.name} by {interaction.user}")

    # ── /admin unrestrict ─────────────────────────────────────────────────

    @admin.command(name="unrestrict", description="Remove role restriction from a command")
    @app_commands.describe(command_name="Command name to unrestrict")
    @app_commands.check(lambda i: _is_admin(i))
    async def unrestrict(self, interaction: discord.Interaction, command_name: str):
        state = _load()
        restrs = state.setdefault("command_restrictions", {})
        if command_name not in restrs:
            await interaction.response.send_message(
                f"⚠️ `/{command_name}` has no restriction set.", ephemeral=True
            )
            return
        del restrs[command_name]
        _save(state)
        msg = f"🔓 `/{command_name}` restriction removed — all members can use it."
        await interaction.response.send_message(msg, ephemeral=True)
        await _audit(self.bot, "Restriction Removed", msg, interaction.user, OK_CLR)
        log.event("admin", f"/{command_name} unrestricted by {interaction.user}")

    # ── /admin setlog ─────────────────────────────────────────────────────

    @admin.command(name="setlog", description="Set the channel where admin actions are logged")
    @app_commands.describe(channel="The channel for admin audit logs")
    @app_commands.check(lambda i: _is_admin(i))
    async def setlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        state = _load()
        state["audit_channel_id"] = str(channel.id)
        _save(state)
        embed = discord.Embed(
            description=f"✅ Admin audit log set to {channel.mention}.\nAll admin actions will be recorded there.",
            color=OK_CLR
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await _audit(self.bot, "Audit Log Configured", f"Logs → {channel.mention}", interaction.user, OK_CLR)
        log.event("admin", f"Audit log → #{channel.name} by {interaction.user}")

    # ── /admin announce ───────────────────────────────────────────────────

    @admin.command(name="announce", description="Post an official MINNAL admin announcement to a channel")
    @app_commands.describe(
        channel="Target channel",
        title="Announcement title",
        message="Announcement body",
        ping="Whether to ping @everyone"
    )
    @app_commands.check(lambda i: _is_admin(i))
    async def announce(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        message: str,
        ping: bool = False
    ):
        embed = discord.Embed(
            title=f"📢 {title}",
            description=message,
            color=0x7c5cfc,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(
            name=f"MINNAL  ·  Admin Announcement",
            icon_url=self.bot.user.display_avatar.url if self.bot.user else None
        )
        embed.set_footer(text=f"Posted by {interaction.user}")

        content = "@everyone" if ping else None
        await channel.send(content=content, embed=embed)
        await interaction.response.send_message(
            f"✅ Announcement posted to {channel.mention}.", ephemeral=True
        )
        await _audit(
            self.bot,
            "Announcement Posted",
            f"Channel: {channel.mention}\n**{title}**\n{message[:200]}",
            interaction.user,
            WARN_CLR
        )
        log.event("admin", f"Announcement in #{channel.name} by {interaction.user}: {title}")

    # ── Catch check failures on any /admin subcommand ─────────────────────

    @commands.Cog.listener()
    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        # Only handle errors from /admin commands
        cmd = interaction.command
        if cmd is None or not (hasattr(cmd, 'parent') and cmd.parent and cmd.parent.name == "admin"):
            return
        if isinstance(error, (app_commands.CheckFailure, app_commands.MissingPermissions)):
            embed = discord.Embed(
                title="⛔ Administrator Only",
                description=(
                    "This command requires **Administrator** permission.\n"
                    "Contact a server admin if you think this is a mistake."
                ),
                color=LOCK_CLR
            )
            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.InteractionResponded:
                await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(BotControl(bot))
