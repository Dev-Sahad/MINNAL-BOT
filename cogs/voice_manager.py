# =============================================================================
#  cogs/voice_manager.py — SUMMON DOMAIN System
#  Dynamic Voice Channel Manager with Anime Aesthetics
# =============================================================================

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
import asyncio
import json
import os


# Anime-themed domain names
DOMAIN_NAMES = [
    "⚡ Minnal Cave",
    "🩸 Sukuna's Shrine",
    "🌀 Gojo's Infinity",
    "🔥 Itadori's Pit",
    "🌙 Megumi's Realm",
    "💀 Mahito's Domain",
    "⚔️ Yuta's Sanctuary",
    "🌸 Nobara's Garden",
    "🦊 Kurama's Den",
    "👁️ Tobi's Void",
    "🐉 Akatsuki Hideout",
    "❄️ Aizen's Throne",
    "🌊 Luffy's Sunny",
    "⚡ Zeus's Olympus",
    "🌑 Madara's Tomb",
    "🔮 Saitama's Cave",
    "🗡️ Tanjiro's Forge",
    "🌪️ Naruto's Vortex"
]

# Persistent storage paths
DATA_DIR = "data"
DOMAINS_FILE = os.path.join(DATA_DIR, "active_domains.json")


class SummonDomain(commands.Cog):
    """⚡ Dynamic Voice Channel System with Domain Expansion"""
    
    def __init__(self, bot):
        self.bot = bot
        self.trigger_channel_id = int(os.getenv('VC_TRIGGER_ID', '0'))
        self.active_domains = {}
        
        # Ensure data directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        self._load_domains()
    
    def _load_domains(self):
        """Load active domains from file"""
        try:
            if os.path.exists(DOMAINS_FILE):
                with open(DOMAINS_FILE, 'r') as f:
                    data = json.load(f)
                    self.active_domains = {int(k): v for k, v in data.items()}
                    print(f"⚡ Loaded {len(self.active_domains)} active domains", flush=True)
        except Exception as e:
            print(f"⚠️ Could not load domains: {e}", flush=True)
            self.active_domains = {}
    
    def _save_domains(self):
        """Save active domains to file"""
        try:
            data = {str(k): v for k, v in self.active_domains.items()}
            with open(DOMAINS_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"⚠️ Could not save domains: {e}", flush=True)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state changes"""
        if member.bot:
            return
        
        # User joined trigger channel
        if (after.channel and 
            after.channel.id == self.trigger_channel_id and
            (before.channel is None or before.channel.id != self.trigger_channel_id)):
            await self._create_domain(member, after.channel)
        
        # User left a domain - check if empty
        if before.channel and before.channel.id in self.active_domains:
            await asyncio.sleep(1)
            if before.channel and len(before.channel.members) == 0:
                await self._delete_domain(before.channel)
    
    async def _create_domain(self, member, trigger_channel):
        """Create a new voice domain for the user"""
        try:
            guild = trigger_channel.guild
            category = trigger_channel.category
            
            domain_name = random.choice(DOMAIN_NAMES)
            full_name = f"{domain_name} - {member.display_name}"
            
            # Set permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    connect=True, speak=True, view_channel=True
                ),
                member: discord.PermissionOverwrite(
                    connect=True, speak=True, manage_channels=True,
                    move_members=True, mute_members=True,
                    deafen_members=True, priority_speaker=True
                ),
                guild.me: discord.PermissionOverwrite(
                    connect=True, manage_channels=True, move_members=True
                )
            }
            
            new_channel = await guild.create_voice_channel(
                name=full_name,
                category=category,
                overwrites=overwrites,
                reason=f"Summon Domain for {member.name}"
            )
            
            await member.move_to(new_channel)
            
            self.active_domains[new_channel.id] = {
                "owner_id": member.id,
                "guild_id": guild.id
            }
            self._save_domains()
            
            print(f"⚡ Domain created: {full_name}", flush=True)
            
            # Send notification
            try:
                notif_channel = guild.system_channel
                if notif_channel and notif_channel.permissions_for(guild.me).send_messages:
                    embed = discord.Embed(
                        title="⚡ DOMAIN EXPANSION",
                        description=f"{member.mention} has summoned\n# {domain_name}",
                        color=discord.Color.purple(),
                        timestamp=datetime.utcnow()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text="Use /domain commands to manage your domain")
                    await notif_channel.send(embed=embed, delete_after=30)
            except Exception:
                pass
        
        except Exception as e:
            print(f"❌ Error creating domain: {e}", flush=True)
    
    async def _delete_domain(self, channel):
        """Delete an empty domain"""
        try:
            if channel.id not in self.active_domains:
                return
            
            await channel.delete(reason="Domain empty - auto cleanup")
            self.active_domains.pop(channel.id, None)
            self._save_domains()
            
            print(f"🧹 Domain deleted: {channel.name}", flush=True)
        
        except discord.NotFound:
            self.active_domains.pop(channel.id, None)
            self._save_domains()
        except Exception as e:
            print(f"❌ Error deleting domain: {e}", flush=True)
    
    @app_commands.command(name="setdomaintrigger", description="Set the voice channel that creates domains")
    @app_commands.describe(channel="The voice channel users join to create a domain")
    async def setdomaintrigger(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Set the trigger channel for domain creation"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Admin only!", ephemeral=True)
            return
        
        self.trigger_channel_id = channel.id
        
        embed = discord.Embed(
            title="⚡ Trigger Channel Set",
            description=f"Trigger: {channel.mention}\n\nUsers joining will summon domains!",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="💡 Tip",
            value=f"Add `VC_TRIGGER_ID = {channel.id}` to Railway variables for permanent setting",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="domainrename", description="Rename your domain")
    @app_commands.describe(new_name="The new name for your domain")
    async def domain_rename(self, interaction: discord.Interaction, new_name: str):
        """Rename your domain (owner only)"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You're not in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        
        if channel.id not in self.active_domains:
            await interaction.response.send_message("❌ This is not a Summon Domain!", ephemeral=True)
            return
        
        if self.active_domains[channel.id]["owner_id"] != interaction.user.id:
            await interaction.response.send_message("⛔ Only the Domain Owner can rename!", ephemeral=True)
            return
        
        try:
            await channel.edit(name=new_name[:100])
            embed = discord.Embed(
                title="✏️ Domain Renamed",
                description=f"New name: **{new_name}**",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="domainkick", description="Kick someone from your domain")
    @app_commands.describe(member="The user to kick from your domain")
    async def domain_kick(self, interaction: discord.Interaction, member: discord.Member):
        """Kick a user from your domain (owner only)"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You're not in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        
        if channel.id not in self.active_domains:
            await interaction.response.send_message("❌ This is not a Summon Domain!", ephemeral=True)
            return
        
        if self.active_domains[channel.id]["owner_id"] != interaction.user.id:
            await interaction.response.send_message("⛔ Only the Domain Owner can kick!", ephemeral=True)
            return
        
        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ Can't kick yourself!", ephemeral=True)
            return
        
        if not member.voice or member.voice.channel != channel:
            await interaction.response.send_message(f"❌ {member.mention} is not in your domain!", ephemeral=True)
            return
        
        try:
            await member.move_to(None)
            embed = discord.Embed(
                title="🚫 Domain Banishment",
                description=f"{member.mention} has been kicked from your domain!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="domainlock", description="Lock your domain (no new joins)")
    async def domain_lock(self, interaction: discord.Interaction):
        """Lock your domain"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You're not in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        
        if channel.id not in self.active_domains:
            await interaction.response.send_message("❌ This is not a Summon Domain!", ephemeral=True)
            return
        
        if self.active_domains[channel.id]["owner_id"] != interaction.user.id:
            await interaction.response.send_message("⛔ Only the Domain Owner can lock!", ephemeral=True)
            return
        
        try:
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            embed = discord.Embed(
                title="🔒 Domain Locked",
                description="Your domain is now locked!",
                color=discord.Color.dark_purple()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="domainunlock", description="Unlock your domain")
    async def domain_unlock(self, interaction: discord.Interaction):
        """Unlock your domain"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You're not in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        
        if channel.id not in self.active_domains:
            await interaction.response.send_message("❌ This is not a Summon Domain!", ephemeral=True)
            return
        
        if self.active_domains[channel.id]["owner_id"] != interaction.user.id:
            await interaction.response.send_message("⛔ Only the Domain Owner can unlock!", ephemeral=True)
            return
        
        try:
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            embed = discord.Embed(
                title="🔓 Domain Unlocked",
                description="Your domain is now open!",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="domaininfo", description="Show information about your domain")
    async def domain_info(self, interaction: discord.Interaction):
        """Show domain information"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You're not in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        
        if channel.id not in self.active_domains:
            await interaction.response.send_message("❌ This is not a Summon Domain!", ephemeral=True)
            return
        
        owner_id = self.active_domains[channel.id]["owner_id"]
        owner = interaction.guild.get_member(owner_id)
        
        embed = discord.Embed(
            title="⚡ Domain Information",
            description=f"**{channel.name}**",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="👑 Owner", value=owner.mention if owner else "Unknown", inline=True)
        embed.add_field(name="👥 Members", value=str(len(channel.members)), inline=True)
        embed.add_field(name="🔊 Bitrate", value=f"{channel.bitrate // 1000}kbps", inline=True)
        
        if channel.members:
            members_list = "\n".join([f"• {m.display_name}" for m in channel.members[:10]])
            embed.add_field(name="📋 Connected", value=members_list, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="listdomains", description="List all active domains in this server")
    async def list_domains(self, interaction: discord.Interaction):
        """List all active domains"""
        guild_domains = [
            (channel_id, data)
            for channel_id, data in self.active_domains.items()
            if data["guild_id"] == interaction.guild.id
        ]
        
        if not guild_domains:
            await interaction.response.send_message("❌ No active domains in this server!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚡ Active Domains",
            description=f"**{len(guild_domains)}** domain(s) currently active",
            color=discord.Color.purple()
        )
        
        for channel_id, data in guild_domains[:25]:
            channel = interaction.guild.get_channel(channel_id)
            owner = interaction.guild.get_member(data["owner_id"])
            if channel:
                embed.add_field(
                    name=channel.name,
                    value=f"👑 {owner.mention if owner else 'Unknown'}\n👥 {len(channel.members)} members",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(SummonDomain(bot))