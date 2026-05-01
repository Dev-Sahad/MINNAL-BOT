# =============================================================================
#  cogs/admin.py — MINNAL Control Center
# =============================================================================

import discord
from discord import app_commands, ui
from discord.ext import commands
from datetime import datetime
import config
import asyncio

# Check if is_admin check exists, otherwise we define a simple version
try:
    from cogs.checks import is_admin
except ImportError:
    def is_admin():
        async def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id in config.DEVELOPER_IDS or interaction.permissions.administrator
        return app_commands.check(predicate)

# ── Modals ──────────────────────────────────────────────────────────────────

class ImageModal(ui.Modal):
    def __init__(self, title: str, config_key: str):
        super().__init__(title=title, timeout=120)
        self._config_key = config_key

    url_input = ui.TextInput(label="Image URL", placeholder="Paste direct link...", style=discord.TextStyle.long, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        value = self.url_input.value.strip()
        setattr(config, self._config_key, None if value.lower() == 'clear' else value)
        await interaction.response.send_message(f"✅ `{self._config_key}` updated.", ephemeral=True)

# ── The Master Admin Panel ──────────────────────────────────────────────────

class AdminPanelView(ui.View):
    def __init__(self, guild_id: int = None):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in config.DEVELOPER_IDS: return True
        guild = interaction.guild or interaction.client.get_guild(self.guild_id)
        if guild and (interaction.user.id == guild.owner_id or interaction.user.guild_permissions.administrator):
            return True
        await interaction.response.send_message("⛔ Administrator clearance required.", ephemeral=True)
        return False

    # ── Row 0: Aesthetic Controls ──
    @ui.button(label="🖼️ Welcome Image", style=discord.ButtonStyle.primary, row=0)
    async def welcome_image(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ImageModal("Set Welcome Image", "WELCOME_IMAGE_URL"))

    @ui.button(label="🔔 Toggle Auto-DM", style=discord.ButtonStyle.success, row=0)
    async def toggle_dm(self, interaction: discord.Interaction, button: ui.Button):
        config.DM_JOIN_ENABLED = not config.DM_JOIN_ENABLED
        await interaction.response.send_message(f"Auto-DM: {'✅ Enabled' if config.DM_JOIN_ENABLED else '⛔ Disabled'}", ephemeral=True)

    # ── Row 1: Core Channel Setup ──
    @ui.button(label="👋 Welcome Ch", style=discord.ButtonStyle.secondary, row=1)
    async def set_welcome(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Use `/welcome #channel` to update permanently.", ephemeral=True)

    @ui.button(label="🎮 Game Ch", style=discord.ButtonStyle.secondary, row=1)
    async def set_game(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Use `/gamechannel #channel` to update permanently.", ephemeral=True)

    # ── Row 2: MINNAL Security Deployment ──
    @ui.button(label="⚡ Deploy Verify", style=discord.ButtonStyle.success, row=2, emoji="🛡️")
    async def deploy_verify(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild or interaction.client.get_guild(self.guild_id)
        channel = guild.get_channel(config.WELCOME_CHANNEL_ID)
        if not channel: return await interaction.response.send_message("❌ Welcome channel not set.", ephemeral=True)
        
        from cogs.verify import VerifyView
        embed = discord.Embed(title="` 💠 ` **IDENTITY VERIFICATION**", description="Click below to gain access.", color=0x2f3136)
        await channel.send(embed=embed, view=VerifyView())
        await interaction.response.send_message(f"✅ Verification deployed to {channel.mention}", ephemeral=True)

    @ui.button(label="🎫 Deploy Tickets", style=discord.ButtonStyle.primary, row=2, emoji="🎫")
    async def deploy_tickets(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild or interaction.client.get_guild(self.guild_id)
        channel = guild.get_channel(getattr(config, 'TICKET_CHANNEL_ID', config.WELCOME_CHANNEL_ID))
        
        from cogs.tickets import TicketStarter
        embed = discord.Embed(title="🎫 **SUPPORT CENTER**", description="Click to open a private ticket.", color=0x2f3136)
        await channel.send(embed=embed, view=TicketStarter())
        await interaction.response.send_message(f"✅ Tickets deployed to {channel.mention}", ephemeral=True)

    # ── Row 3: Emergency Lockdown ──
    @ui.button(label="🚨 GLOBAL LOCKDOWN", style=discord.ButtonStyle.danger, row=3)
    async def lockdown(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild or interaction.client.get_guild(self.guild_id)
        channel = guild.get_channel(config.WELCOME_CHANNEL_ID)
        await channel.set_permissions(guild.default_role, send_messages=False)
        await interaction.response.send_message(f"⚠️ **LOCKDOWN ACTIVE:** {channel.mention} restricted.", ephemeral=True)

# ── Build Embed Utility ──

def build_admin_panel_embed(guild: discord.Guild) -> discord.Embed:
    embed = discord.Embed(title="⚙️ MINNAL SYSTEM PANEL", color=0x2f3136, timestamp=datetime.utcnow())
    embed.add_field(name="System Status", value="🟢 Online / Secure", inline=True)
    embed.add_field(name="Auto-DM", value="✅ ON" if config.DM_JOIN_ENABLED else "❌ OFF", inline=True)
    embed.add_field(name="Active Guild", value=f"`{guild.name}`", inline=False)
    embed.set_footer(text=f"Authorized Admin: {config.DEVELOPER}")
    return embed

# ── The Cog ──

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="panel", description="Open the MINNAL Admin Settings Panel")
    @is_admin()
    async def panel(self, interaction: discord.Interaction):
        embed = build_admin_panel_embed(interaction.guild)
        await interaction.response.send_message(embed=embed, view=AdminPanelView(interaction.guild.id), ephemeral=True)

    @app_commands.command(name="clear", description="Purge messages")
    @is_admin()
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"⚡ Purged `{amount}` messages.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
