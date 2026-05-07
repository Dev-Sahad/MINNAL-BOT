# =============================================================================
#  cogs/tickets.py — MINNAL Ticket System
#  Beautiful ticket panel with category select, private threads, claim/close.
#  /ticket panel   — drops the panel in a channel (admin only)
#  /ticket setup   — configure staff roles & log channel
# =============================================================================

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
import asyncio

# ── Config ─────────────────────────────────────────────────────────────────
import config
from config_manager import get_setting, set_setting

# Load settings from config_manager
STAFF_ROLE_IDS = get_setting('tickets.staff_role_ids', [config.STAFF_ROLE_ID, 1477254538313470096, 1499490549621850184])
try:
    TICKET_LOG_ID = int(get_setting('tickets.log_channel_id', getattr(config, 'TICKET_LOG_ID', 0)))
except (ValueError, TypeError):
    TICKET_LOG_ID = 0

BRAND_COLOR  = 0x5865F2   # Discord blurple
OPEN_COLOR   = 0x57F287   # green
CLOSE_COLOR  = 0xED4245   # red
CLAIM_COLOR  = 0xFEE75C   # yellow

CATEGORIES = {
    "🆘  General Support":   "support",
    "🐛  Bug Report":        "bug",
    "⚖️  Appeal":             "appeal",
    "🤝  Partnership":       "partner",
    "💬  Other":             "other",
}

CATEGORY_COLORS = {
    "support": 0x5865F2,
    "bug":     0xED4245,
    "appeal":  0xFEE75C,
    "partner": 0x57F287,
    "other":   0xEB459E,
}

# ── Helpers ─────────────────────────────────────────────────────────────────

def is_staff(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True
    role_ids = {r.id for r in member.roles}
    return bool(role_ids & set(STAFF_ROLE_IDS))


# ── Category Select ──────────────────────────────────────────────────────────

class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value, emoji=label.split()[0])
            for label, value in CATEGORIES.items()
        ]
        super().__init__(
            placeholder="Choose a category…",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_category_select"
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        await interaction.response.send_modal(TicketModal(category))


class CategoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategorySelect())

    @discord.ui.button(
        label="Open a Ticket",
        style=discord.ButtonStyle.blurple,
        emoji="🎫",
        custom_id="ticket_open_btn",
        row=1
    )
    async def open_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Show category selector as an ephemeral message
        embed = discord.Embed(
            title="Choose a Category",
            description="Select the type of ticket that best matches your request.",
            color=BRAND_COLOR
        )
        await interaction.response.send_message(embed=embed, view=CategorySelectView(), ephemeral=True)


class CategorySelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(CategorySelect())


# ── Ticket Modal ─────────────────────────────────────────────────────────────

class TicketModal(discord.ui.Modal):
    def __init__(self, category: str):
        label_map = {v: k for k, v in CATEGORIES.items()}
        super().__init__(title=f"Open Ticket — {label_map.get(category, 'Support')}")
        self.category = category

        self.subject = discord.ui.TextInput(
            label="Subject",
            placeholder="Short summary of your issue",
            max_length=100,
            required=True
        )
        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="Give us as much detail as possible…",
            style=discord.TextStyle.long,
            min_length=10,
            max_length=1000,
            required=True
        )
        self.add_item(self.subject)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild  = interaction.guild
        user   = interaction.user
        cat    = self.category

        if not isinstance(interaction.channel, (discord.TextChannel, discord.ForumChannel)):
            return await interaction.followup.send(
                "❌ Tickets can only be opened from a regular text channel or forum.",
                ephemeral=True
            )

        # ── Duplicate Ticket Check ──
        # Check for existing open threads in this channel for this user
        existing = discord.utils.get(interaction.channel.threads, name=f"🎫 {user.name} — {cat}", archived=False)
        if existing:
            return await interaction.followup.send(
                f"❌ You already have an open ticket in this category: {existing.mention}",
                ephemeral=True
            )

        try:
            # Create private thread from the ticket channel
            thread = await interaction.channel.create_thread(
                name=f"🎫 {user.name} — {cat}",
                type=discord.ChannelType.private_thread,
                auto_archive_duration=1440,
                invitable=False
            )
        except discord.Forbidden:
            return await interaction.followup.send(
                "❌ **Missing Permissions**: I don't have permission to create private threads in this channel.",
                ephemeral=True
            )
        except Exception as e:
            return await interaction.followup.send(
                f"❌ **Error**: Failed to create ticket. ({str(e)})",
                ephemeral=True
            )

        await thread.add_user(user)

        # ── Main ticket embed ──
        label_map = {v: k for k, v in CATEGORIES.items()}
        color = CATEGORY_COLORS.get(cat, BRAND_COLOR)
        embed = discord.Embed(
            title=f"🎫  Ticket — {label_map.get(cat, 'Support')}",
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_author(
            name=f"{user.display_name}  ({user.id})",
            icon_url=user.display_avatar.url
        )
        embed.add_field(name="📌 Subject",     value=self.subject.value,     inline=False)
        embed.add_field(name="📝 Description", value=self.description.value, inline=False)
        embed.add_field(name="👤 Opened by",   value=user.mention,           inline=True)
        embed.add_field(name="🏷️ Category",    value=label_map.get(cat, cat).strip(), inline=True)
        embed.add_field(name="📅 Created",     value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
        embed.set_footer(text="MINNAL Support  •  Staff will be with you shortly")
        embed.set_thumbnail(url=user.display_avatar.url)

        # Ping staff roles
        staff_mentions = " ".join(f"<@&{r}>" for r in STAFF_ROLE_IDS)
        await thread.send(content=staff_mentions, embed=embed, view=TicketControlView())

        # ── Logging ──
        if TICKET_LOG_ID:
            log_chan = guild.get_channel(TICKET_LOG_ID)
            if log_chan:
                log_embed = discord.Embed(
                    title="🎫 Ticket Opened",
                    description=f"**User:** {user.mention} ({user.id})\n**Category:** {cat}\n**Thread:** {thread.mention}",
                    color=OPEN_COLOR,
                    timestamp=datetime.now(timezone.utc)
                )
                await log_chan.send(embed=log_embed)

        # ── Confirm to user ──
        done = discord.Embed(
            description=f"✅ Your ticket has been created → {thread.mention}\nOur staff will assist you shortly.",
            color=OPEN_COLOR
        )
        await interaction.followup.send(embed=done, ephemeral=True)


# ── Ticket Control (inside thread) ───────────────────────────────────────────

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="✋", custom_id="ticket_claim_btn")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("⛔ Only staff can claim tickets.", ephemeral=True)
            return
        button.disabled = True
        button.label = f"Claimed by {interaction.user.display_name}"
        button.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)

        embed = discord.Embed(
            description=f"✋ **{interaction.user.mention}** has claimed this ticket and will assist you!",
            color=CLAIM_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        await interaction.channel.send(embed=embed)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close_btn")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        # check if member is staff
        if not is_staff(interaction.user):
            # check if member is the ticket opener
            if interaction.user not in interaction.channel.members:
                await interaction.response.send_message("⛔ You cannot close this ticket.", ephemeral=True)
                return

        await interaction.response.send_message(
            embed=discord.Embed(
                title="🔒 Close this ticket?",
                description="This will archive and delete the thread. This action cannot be undone.",
                color=CLOSE_COLOR
            ),
            view=ConfirmCloseView(),
            ephemeral=True
        )


class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="Yes, Close it", style=discord.ButtonStyle.danger, emoji="🔒")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # ── Logging ──
        if TICKET_LOG_ID:
            guild = interaction.guild
            log_chan = guild.get_channel(TICKET_LOG_ID)
            if log_chan:
                log_embed = discord.Embed(
                    title="🔒 Ticket Closed",
                    description=f"**Thread:** {interaction.channel.name}\n**Closed by:** {interaction.user.mention} ({interaction.user.id})",
                    color=CLOSE_COLOR,
                    timestamp=datetime.now(timezone.utc)
                )
                await log_chan.send(embed=log_embed)

        closing = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"Closed by **{interaction.user.mention}**. Deleting in 5 seconds…",
            color=CLOSE_COLOR,
            timestamp=datetime.now(timezone.utc)
        )
        await interaction.channel.send(embed=closing)
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(description="Cancelled — ticket remains open.", color=OPEN_COLOR),
            view=None
        )


# ── Panel Embed ───────────────────────────────────────────────────────────────

def build_panel_embed(guild: discord.Guild) -> discord.Embed:
    embed = discord.Embed(
        title="🎫  MINNAL Support Center",
        description=(
            "Need help? Have an issue? Want to report something?\n"
            "We've got you covered — open a private ticket below.\n\n"
            "**Available Categories**\n"
            + "\n".join(f"{emoji}  {label.split('  ')[1]}" for emoji, label in [
                ("🆘", "General Support"),
                ("🐛", "Bug Report"),
                ("⚖️", "Appeal"),
                ("🤝", "Partnership"),
                ("💬", "Other"),
            ])
            + "\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 Your ticket is **private** — only you and staff can see it.\n"
            "⚡ Average response time: **under 24 hours**"
        ),
        color=BRAND_COLOR
    )
    embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
    embed.set_footer(text="MINNAL Support  •  Click the button below to get started")
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    return embed


# ── Cog ───────────────────────────────────────────────────────────────────────

class MinnalTickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CategoryView())
        self.bot.add_view(TicketControlView())
        self.bot.add_view(ConfirmCloseView())

    ticket = app_commands.Group(name="ticket", description="🎫 Ticket system management")

    @ticket.command(name="panel", description="Post the ticket panel in this channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        embed = build_panel_embed(interaction.guild)
        await interaction.channel.send(embed=embed, view=CategoryView())
        await interaction.response.send_message("✅ Ticket panel posted!", ephemeral=True)

    @app_commands.command(name="ticket_panel", description="Post the ticket panel in this channel (Alias)")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_panel_alias(self, interaction: discord.Interaction):
        """Direct alias for /ticket panel"""
        embed = build_panel_embed(interaction.guild)
        await interaction.channel.send(embed=embed, view=CategoryView())
        await interaction.response.send_message("✅ Ticket panel posted!", ephemeral=True)

    @ticket.command(name="setup", description="Configure the ticket system settings")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(staff_role="The role that handles tickets", log_channel="Channel for ticket logs")
    async def setup(self, interaction: discord.Interaction, staff_role: discord.Role = None, log_channel: discord.TextChannel = None):
        global STAFF_ROLE_IDS, TICKET_LOG_ID
        
        if not staff_role and not log_channel:
            return await interaction.response.send_message("❌ Please provide at least one setting to update.", ephemeral=True)
            
        if staff_role:
            if staff_role.id not in STAFF_ROLE_IDS:
                STAFF_ROLE_IDS.append(staff_role.id)
                set_setting('tickets.staff_role_ids', STAFF_ROLE_IDS)
            msg = f"✅ Added {staff_role.mention} to staff roles."
        else:
            msg = "✅ Updated settings."
            
        if log_channel:
            TICKET_LOG_ID = log_channel.id
            set_setting('tickets.log_channel_id', TICKET_LOG_ID)
            msg += f"\n✅ Ticket logs will now be sent to {log_channel.mention}."
            
        await interaction.response.send_message(msg, ephemeral=True)

    @ticket.command(name="add", description="Add a user to the current ticket thread")
    @app_commands.describe(user="User to add")
    async def add_user(self, interaction: discord.Interaction, user: discord.Member):
        if not is_staff(interaction.user):
            await interaction.response.send_message("⛔ Staff only.", ephemeral=True)
            return
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("❌ Use this inside a ticket thread.", ephemeral=True)
            return
        await interaction.channel.add_user(user)
        await interaction.response.send_message(
            embed=discord.Embed(description=f"✅ Added {user.mention} to this ticket.", color=OPEN_COLOR),
            ephemeral=True
        )

    @ticket.command(name="close", description="Close and delete this ticket thread")
    async def close(self, interaction: discord.Interaction):
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("❌ Use this inside a ticket thread.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🔒 Close this ticket?",
                description="This will delete the thread permanently.",
                color=CLOSE_COLOR
            ),
            view=ConfirmCloseView(),
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(MinnalTickets(bot))
