import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput

# --- SETTINGS ---
TICKET_CHANNEL_ID = 1463953874019680276  # The channel where the "Open Ticket" button lives
STAFF_ROLE_ID = 1477254538313470096, 1499490549621850184    # Admin/Sub Admin role allowed to close tickets

class CloseTicketView(discord.ui.View):
    """The view inside the thread containing the 'Close' button."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close & Delete Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn", emoji="🔒")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the person clicking is Staff
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("⚡ Only Staff can close this ticket!", ephemeral=True)

        await interaction.response.send_message("⚡ Closing ticket and deleting thread in 3 seconds...")
        
        # Small delay so the user can see the message
        import asyncio
        await asyncio.sleep(3)
        
        # Delete the thread
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.delete()

class TicketModal(discord.ui.Modal, title="Support Ticket"):
    """The popup window for the user to describe their issue."""
    issue = discord.ui.TextInput(
        label="What do you need help with?",
        placeholder="Describe your issue here...",
        style=discord.TextStyle.long,
        min_length=10,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Create a thread from the message in the ticket channel
        thread = await interaction.channel.create_thread(
            name=f"ticket-{interaction.user.name}",
            type=discord.ChannelType.private_thread, # Keeps it private
            auto_archive_duration=60
        )
        
        # Add the user and staff to the thread
        await thread.add_user(interaction.user)
        
        embed = discord.Embed(
            title="⚡ MINNAL | Support Ticket",
            description=f"**User:** {interaction.user.mention}\n**Issue:** {self.issue.value}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Staff will be with you shortly. Use the button below to finish.")

        await thread.send(content=f"<@&{STAFF_ROLE_ID}>", embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"⚡ Ticket created! Check {thread.mention}", ephemeral=True)

class TicketStarterView(discord.ui.View):
    """The view for the permanent 'Open Ticket' button."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Support Ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket_btn", emoji="🎫")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

class MinnalTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Register both views so they work after bot restarts
        self.bot.add_view(TicketStarterView())
        self.bot.add_view(CloseTicketView())
        print("⚡ MINNAL Ticket System is online!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        """Sends the initial 'Open Ticket' message"""
        embed = discord.Embed(
            title="🎫 Support & Help",
            description=(
                "Need help with a project, role, or server issue?\n\n"
                "Click the button below to open a private ticket. "
                "Our staff will assist you as fast as lightning ⚡."
            ),
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=TicketStarterView())

async def setup(bot):
    await bot.add_cog(MinnalTickets(bot))
