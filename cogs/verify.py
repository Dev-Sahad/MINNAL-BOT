import discord
from discord.ext import commands
from discord.ui import Button, View

# --- SETTINGS ---
VERIFIED_ROLE_ID = 1499465467402653767 

class MinnalVerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verify with Minnal", 
        style=discord.ButtonStyle.green, 
        custom_id="minnal_verify_persistent", 
        emoji="⚡"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        
        if not role:
            return await interaction.response.send_message("❌ Role error. Contact Admin.", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.response.send_message("⚡ Already verified!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("⚡ Verified!", ephemeral=True)
            
            # Send DM after successful verification
            try:
                embed = discord.Embed(
                    title="⚡ Access Granted!",
                    description=(
                        f"Welcome to the SAHAD IS LIVE Server, **{interaction.user.name}**!\n\n"
                        "You now have full access to the server. Check out the channels "
                        "and stay active to climb the ranks."
                    ),
                    color=discord.Color.gold()
                )
                await interaction.user.send(embed=embed)
            except discord.Forbidden:
                # This happens if the user has DMs closed
                pass

class MinnalSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(MinnalVerifyView())
        pass  # startup logged by discord_bot.py

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Sends a DM when a user first joins the server"""
        try:
            embed = discord.Embed(
                title="⚡ Welcome to the Fam!",
                description=(
                    f"Hey {member.mention}, welcome to the server!\n\n"
                    "To see the rest of the channels, please go to the **<#1465673172656586873>** "
                    "channel and click the button. **MINNAL** will handle the rest."
                ),
                color=discord.Color.yellow()
            )
            embed.set_footer(text="See you inside!")
            await member.send(embed=embed)
        except discord.Forbidden:
            # If DMs are closed, the bot won't crash
            print(f"Could not DM {member.name} because their DMs are closed.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_minnal(self, ctx):
        embed = discord.Embed(
            title="⚡ MINNAL | System Verification",
            description="Click the button below to get your verified role instantly.",
            color=discord.Color.yellow()
        )
        await ctx.send(embed=embed, view=MinnalVerifyView())

async def setup(bot):
    await bot.add_cog(MinnalSystem(bot))
