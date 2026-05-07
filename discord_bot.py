# =============================================================================
#  discord_bot.py — MINNAL Core Entry Point
# =============================================================================

import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import config
import logger as log

# Attempt to import Persistent Views
try:
    from cogs.tickets import CategoryView, TicketControlView, ConfirmCloseView
    from cogs.verify import MinnalVerifyView
except ImportError:
    CategoryView, TicketControlView, ConfirmCloseView, MinnalVerifyView = None, None, None, None

load_dotenv()

# ── BOT INSTANCE ──────────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# ── MODULE REGISTRY ───────────────────────────────────────────────────────────
COGS = [
    'cogs.bot_control',                                              # ← first: installs global check
    'cogs.dashboard', 'cogs.admin', 'cogs.music', 'cogs.fun',
    'cogs.info', 'cogs.economy', 'cogs.giveaways', 'cogs.utilities',
    'cogs.voice_manager', 'cogs.web_bridge', 'cogs.rizz_engine',
    'cogs.voice_features', 'cogs.memes',
    'cogs.verify', 'cogs.autorole', 'cogs.ghostping',
    'cogs.stats', 'cogs.tickets', 'cogs.sentinel', 'cogs.codepilot',
    'cogs.log_relay', 'cogs.welcome', 'cogs.anime', 'cogs.levels', 'cogs.help',
    'cogs.watchlist',
    'cogs.ai_chat',
]

COG_DESC = {
    'cogs.bot_control':    'Admin lock · feature toggles · audit log',
    'cogs.dashboard':      'Web admin panel & API server',
    'cogs.admin':          'Server control center',
    'cogs.music':          'Voice & music player',
    'cogs.fun':            'Fun commands & games',
    'cogs.info':           'Bot info & command directory',
    'cogs.economy':        'Virtual economy & coins',
    'cogs.giveaways':      'Giveaway system',
    'cogs.utilities':      'Utility tools & reminders',
    'cogs.voice_manager':  'Dynamic voice domains',
    'cogs.web_bridge':     'Webhook & stats bridge',
    'cogs.rizz_engine':    'Status rotation engine',
    'cogs.voice_features': 'Anime voice spells',
    'cogs.memes':          'Auto meme poster',
    'cogs.verify':         'Member verification',
    'cogs.autorole':       'Auto role assignment',
    'cogs.ghostping':      'Ghost ping detector',
    'cogs.stats':          'Server statistics',
    'cogs.tickets':        'Ticket system',
    'cogs.sentinel':       'Server sentinel guard',
    'cogs.codepilot':      'AI code assistant',
    'cogs.log_relay':      'Railway → Discord log relay',
    'cogs.welcome':        'Welcome & goodbye system',
    'cogs.anime':          'Anime search & daily posts',
    'cogs.levels':         'XP & level system',
    'cogs.help':           'Command catalogue',
    'cogs.watchlist':      'Personal anime watchlist',
    'cogs.ai_chat':        'Claude AI chat channel',
}

# ── GLOBAL INTERACTION CHECK ──────────────────────────────────────────────────
# Runs before every slash command. Enforces:
#   1. Bot lock    — only admins get through when locked
#   2. Feature off — block commands belonging to a disabled feature
#   3. Restriction — block commands restricted to a role the user lacks

def _is_admin_user(interaction: discord.Interaction) -> bool:
    if interaction.user.id in config.DEVELOPER_IDS:
        return True
    if interaction.guild and interaction.guild.owner_id == interaction.user.id:
        return True
    member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
    return bool(member and member.guild_permissions.administrator)


async def global_interaction_check(interaction: discord.Interaction) -> bool:
    from cogs.bot_control import (
        is_bot_locked, get_lock_reason,
        get_disabled_features, get_command_restrictions
    )

    # Always pass through for admins / DMs
    if not interaction.guild or _is_admin_user(interaction):
        return True

    cmd_name = interaction.command.name if interaction.command else ""

    # ── 1. Bot Lock ───────────────────────────────────────────────────────
    if is_bot_locked():
        embed = discord.Embed(
            title="🔒 Bot Locked",
            description=(
                f"**{get_lock_reason()}**\n\n"
                "The bot is currently restricted to administrators only.\n"
                "Please wait for an admin to unlock it."
            ),
            color=0xff4757
        )
        embed.set_footer(text="MINNAL  ·  Admin Control")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False

    # ── 2. Disabled Features ──────────────────────────────────────────────
    cog_obj  = interaction.command.binding if interaction.command else None
    cog_name = type(cog_obj).__module__.split(".")[-1] if cog_obj else ""
    disabled = get_disabled_features()

    if cog_name in disabled:
        from cogs.bot_control import FEATURES
        label = FEATURES.get(cog_name, cog_name)
        embed = discord.Embed(
            title="🔴 Feature Disabled",
            description=f"**{label}** has been turned off by an admin.",
            color=0xff4757
        )
        embed.set_footer(text="Contact a server admin to re-enable this feature.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False

    # ── 3. Command Role Restrictions ──────────────────────────────────────
    restrictions = get_command_restrictions()
    if cmd_name in restrictions:
        required_role_id = int(restrictions[cmd_name])
        member = interaction.guild.get_member(interaction.user.id)
        if member and not any(r.id == required_role_id for r in member.roles):
            role = interaction.guild.get_role(required_role_id)
            role_name = role.name if role else f"ID {required_role_id}"
            embed = discord.Embed(
                title="🔐 Restricted Command",
                description=(
                    f"`/{cmd_name}` requires the **{role_name}** role.\n"
                    "Ask an admin if you think you should have access."
                ),
                color=0xffa502
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False

    return True


# ── STARTUP & SYNC ────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    # Wire up global interaction check
    bot.tree.interaction_check = global_interaction_check

    if CategoryView:
        bot.add_view(CategoryView())
    if TicketControlView:
        bot.add_view(TicketControlView())
    if ConfirmCloseView:
        bot.add_view(ConfirmCloseView())
    if MinnalVerifyView:
        bot.add_view(MinnalVerifyView())

    try:
        synced = await bot.tree.sync()
    except Exception as e:
        log.error("SYNC", str(e))
        synced = []

    log.ready(
        bot=str(bot.user),
        guilds=len(bot.guilds),
        commands=len(synced),
        latency=f"{round(bot.latency * 1000)}ms"
    )

# ── MAIN EXECUTION ────────────────────────────────────────────────────────────

async def main():
    log.banner()

    async with bot:
        log.section(f"Loading {len(COGS)} modules")

        ok_count, fail_count = 0, 0
        for cog in COGS:
            tag  = cog.split(".")[-1]
            desc = COG_DESC.get(cog, "")
            try:
                await bot.load_extension(cog)
                log.ok(tag, desc)
                ok_count += 1
            except Exception as e:
                log.fail(tag, str(e)[:65])
                fail_count += 1

        print()
        if fail_count:
            log.warn("MODULES", f"{ok_count} loaded  │  {fail_count} failed")
        else:
            log.ok("ALL MODULES", f"{ok_count} loaded with no errors ✓")
        print()

        TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n  [OFFLINE]  Shutdown complete.\n")
