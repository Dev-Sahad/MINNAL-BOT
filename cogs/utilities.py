# =============================================================================
#  cogs/utilities.py — MINNAL Utility, Birthday & Auto-Role System
# =============================================================================

import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
from datetime import datetime
import json
import os
import config
from cogs.checks import is_admin


class UtilitiesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reaction_roles_file = 'data/reaction_roles.json'
        self.birthdays_file = 'data/birthdays.json'
        self.ensure_data_files()
        self.reaction_roles = self.load_json(self.reaction_roles_file)
        self.birthdays = self.load_json(self.birthdays_file)
        self.birthday_check.start()

    def ensure_data_files(self):
        os.makedirs('data', exist_ok=True)
        for file in [self.reaction_roles_file, self.birthdays_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump({}, f)

    def load_json(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_json(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    # ── Auto-Role Logic ──────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Assigns the default role from config.py on join"""
        role_id = getattr(config, 'AUTO_ROLE_ID', None)
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                except Exception as e:
                    print(f"❌ Auto-Role Error: {e}")

    # ── Reaction Roles ────────────────────────────────────────────────────────
    @app_commands.command(name="reactionrole", description="Create a reaction role message (Admin only)")
    @is_admin()
    async def slash_reactionrole(self, interaction: discord.Interaction, emoji: str, role: discord.Role, description: str):
        embed = discord.Embed(
            title="` 📋 ` **IDENTITY ROLES**",
            description=f"React with {emoji} to get the **{role.name}** role.\n\n> {description}",
            color=0x2f3136
        )
        embed.set_footer(text="Click to toggle role")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction(emoji)
        
        msg_id = str(message.id)
        if msg_id not in self.reaction_roles: self.reaction_roles[msg_id] = {}
        self.reaction_roles[msg_id][emoji] = role.id
        self.save_json(self.reaction_roles_file, self.reaction_roles)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id: return
        msg_id = str(payload.message_id)
        if msg_id in self.reaction_roles:
            emoji = str(payload.emoji)
            if emoji in self.reaction_roles[msg_id]:
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(self.reaction_roles[msg_id][emoji])
                member = guild.get_member(payload.user_id)
                if role and member: await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        msg_id = str(payload.message_id)
        if msg_id in self.reaction_roles:
            emoji = str(payload.emoji)
            if emoji in self.reaction_roles[msg_id]:
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(self.reaction_roles[msg_id][emoji])
                member = guild.get_member(payload.user_id)
                if role and member: await member.remove_roles(role)

    # ── Birthdays ─────────────────────────────────────────────────────────────
    @app_commands.command(name="birthday", description="Set your birthday for a shoutout!")
    async def slash_birthday(self, interaction: discord.Interaction, month: int, day: int):
        if not (1 <= month <= 12 and 1 <= day <= 31):
            return await interaction.response.send_message("❌ Invalid date.", ephemeral=True)
        
        self.birthdays[str(interaction.user.id)] = {'month': month, 'day': day}
        self.save_json(self.birthdays_file, self.birthdays)
        await interaction.response.send_message(f"🎂 Birthday set for **{month}/{day}**!", ephemeral=True)

    @tasks.loop(hours=24)
    async def birthday_check(self):
        now = datetime.utcnow()
        for user_id, bday in self.birthdays.items():
            if bday['month'] == now.month and bday['day'] == now.day:
                for guild in self.bot.guilds:
                    member = guild.get_member(int(user_id))
                    if member:
                        # Priority: Config Welcome Channel -> General -> First available
                        channel_id = getattr(config, 'WELCOME_CHANNEL_ID', None)
                        channel = guild.get_channel(channel_id) or discord.utils.get(guild.text_channels, name="general")
                        if channel:
                            embed = discord.Embed(
                                title="🎉 **HAPPY BIRTHDAY!** 🎂",
                                description=f"Everyone wish {member.mention} a legendary day! 🎈",
                                color=0xFFD700
                            )
                            embed.set_thumbnail(url=member.display_avatar.url)
                            await channel.send(content=f"⚡ {member.mention}", embed=embed)

    @birthday_check.before_loop
    async def before_birthday_check(self):
        await self.bot.wait_until_ready()

    # ── Utility Info ──────────────────────────────────────────────────────────
    @app_commands.command(name="serverinfo", description="⚡ Technical specs of the server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"📡 {guild.name} | Intel", color=0x2f3136, timestamp=datetime.utcnow())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=f"Total: {guild.member_count}", inline=True)
        embed.add_field(name="Boost Level", value=f"Tier {guild.premium_tier}", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="⚡ Profile data on a member")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        embed = discord.Embed(title=f"👤 {target.name}", color=target.color, timestamp=datetime.utcnow())
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Joined", value=f"<t:{int(target.joined_at.timestamp())}:D>", inline=True)
        embed.add_field(name="Account Age", value=f"<t:{int(target.created_at.timestamp())}:R>", inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(UtilitiesCog(bot))
