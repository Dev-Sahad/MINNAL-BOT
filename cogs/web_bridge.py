# =============================================================================
#  cogs/web_bridge.py — Web Panel ↔ Discord Bot Bridge
#  Real-time communication between web panel and Discord bot
# =============================================================================

import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import os
import aiohttp
import asyncio
import secrets


class WebBridgeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_file = 'data/web_config.json'
        self.stats_file = 'data/bot_stats.json'
        self.ensure_data_files()
        self.web_config = self.load_json(self.config_file)
        self.stats_update_task.start()
    
    def ensure_data_files(self):
        """Create data directory and files if they don't exist"""
        os.makedirs('data', exist_ok=True)
        for file in [self.config_file, self.stats_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump({}, f)
    
    def load_json(self, filepath):
        """Load JSON data from file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def save_json(self, filepath, data):
        """Save JSON data to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Save JSON error: {e}", flush=True)
    
    def get_bot_stats(self):
        """Get current bot statistics"""
        return {
            'guilds': len(self.bot.guilds),
            'total_users': sum(g.member_count for g in self.bot.guilds),
            'total_channels': sum(len(g.channels) for g in self.bot.guilds),
            'latency': round(self.bot.latency * 1000),
            'cogs_loaded': len(self.bot.cogs),
            'commands': len(self.bot.tree.get_commands()),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # ── Background Tasks ─────────────────────────────────────────────────────
    
    @tasks.loop(minutes=5)
    async def stats_update_task(self):
        """Update bot stats every 5 minutes"""
        try:
            stats = self.get_bot_stats()
            self.save_json(self.stats_file, stats)
        except Exception as e:
            print(f"Stats update error: {e}", flush=True)
    
    @stats_update_task.before_loop
    async def before_stats_update(self):
        await self.bot.wait_until_ready()
    
    # ── Send Event to Webhook ─────────────────────────────────────────────────
    
    async def send_webhook_event(self, event_type: str, data: dict):
        """Send event to webhook server"""
        webhook_url = self.web_config.get('webhook_url')
        webhook_secret = self.web_config.get('webhook_secret')
        
        if not webhook_url or not webhook_secret:
            return
        
        payload = {
            'event_type': event_type,
            **data
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{webhook_url}/webhook/bot/event",
                    json=payload,
                    headers={'X-Webhook-Secret': webhook_secret}
                ) as resp:
                    if resp.status == 200:
                        print(f"✅ Event '{event_type}' sent to webhook", flush=True)
        except Exception as e:
            print(f"Webhook send error: {e}", flush=True)
    
    # ── Command tracking ──────────────────────────────────────────────────────
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Track command usage"""
        try:
            self.web_config['commands_today'] = self.web_config.get('commands_today', 0) + 1
            self.save_json(self.config_file, self.web_config)
            
            await self.send_webhook_event('command_used', {
                'command_name': ctx.command.name if ctx.command else 'unknown',
                'user': str(ctx.author),
                'channel': str(ctx.channel)
            })
        except Exception as e:
            print(f"Command tracking error: {e}", flush=True)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track member join events"""
        try:
            await self.send_webhook_event('member_join', {
                'user_id': member.id,
                'username': str(member),
                'guild_name': member.guild.name,
                'member_count': member.guild.member_count
            })
        except Exception as e:
            print(f"Member join tracking error: {e}", flush=True)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Track member leave events"""
        try:
            await self.send_webhook_event('member_leave', {
                'user_id': member.id,
                'username': str(member),
                'guild_name': member.guild.name,
                'member_count': member.guild.member_count
            })
        except Exception as e:
            print(f"Member leave tracking error: {e}", flush=True)
    
    # ============= /link - Generate Web Panel Token =============
    
    @app_commands.command(name="link", description="🔗 Get a token to link your web panel")
    async def link(self, interaction: discord.Interaction):
        """Generate a token to connect web panel to bot"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "⛔ You need Administrator permission!",
                ephemeral=True
            )
            return
        
        # Generate a secure token
        token = secrets.token_urlsafe(32)
        
        # Save token in config
        if 'tokens' not in self.web_config:
            self.web_config['tokens'] = {}
        
        self.web_config['tokens'][token] = {
            'guild_id': interaction.guild.id,
            'user_id': interaction.user.id,
            'created': datetime.utcnow().isoformat()
        }
        self.save_json(self.config_file, self.web_config)
        
        embed = discord.Embed(
            title="🔗 Web Panel Connection Token",
            description="Use this token to connect your web panel to the bot",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="🔑 Your Token",
            value=f"```{token}```",
            inline=False
        )
        embed.add_field(
            name="📝 Instructions",
            value=(
                "1. Open https://minnal.up.railway.app\n"
                "2. Login with: `MINNAL@2025`\n"
                "3. Go to **Bot Connection** tab\n"
                "4. Paste the token above\n"
                "5. Click **Connect**"
            ),
            inline=False
        )
        embed.add_field(
            name="⚠️ Security",
            value="Don't share this token with anyone! It expires when bot restarts.",
            inline=False
        )
        embed.set_footer(text="⚡ MINNAL Bot - Web Bridge")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============= /webstats - Show Web Panel Status =============
    
    @app_commands.command(name="webstats", description="📊 Show web panel and bot statistics")
    async def webstats(self, interaction: discord.Interaction):
        """Show current bot/web statistics"""
        await interaction.response.defer(ephemeral=True)
        
        stats = self.get_bot_stats()
        commands_today = self.web_config.get('commands_today', 0)
        
        embed = discord.Embed(
            title="📊 MINNAL Bot Statistics",
            description="Real-time bot and web panel stats",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🏰 Servers", value=str(stats['guilds']), inline=True)
        embed.add_field(name="👥 Users", value=str(stats['total_users']), inline=True)
        embed.add_field(name="📝 Channels", value=str(stats['total_channels']), inline=True)
        embed.add_field(name="🛰️ Latency", value=f"{stats['latency']}ms", inline=True)
        embed.add_field(name="⚙️ Cogs", value=str(stats['cogs_loaded']), inline=True)
        embed.add_field(name="🔧 Commands", value=str(stats['commands']), inline=True)
        embed.add_field(name="📈 Commands Today", value=str(commands_today), inline=True)
        embed.add_field(
            name="🌐 Web Panel",
            value="[Open Panel](https://minnal.up.railway.app)",
            inline=True
        )
        embed.set_footer(text="⚡ MINNAL Bot")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ============= /webpanel - Get Web Panel Link =============
    
    @app_commands.command(name="webpanel", description="🌐 Get the admin web panel link")
    async def webpanel(self, interaction: discord.Interaction):
        """Get web panel access information"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "⛔ Admin only!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🌐 MINNAL Admin Web Panel",
            description="Manage your bot from the web!",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="🔗 Panel URL",
            value="[Open Admin Panel](https://minnal.up.railway.app)",
            inline=False
        )
        embed.add_field(name="🔐 Default Password", value="`MINNAL@2025`", inline=True)
        embed.add_field(
            name="✨ Features",
            value="• Bot Settings\n• Command Management\n• AI Help Desk\n• Export Config",
            inline=False
        )
        embed.add_field(
            name="🔗 Connect Bot",
            value="Use `/link` to get a connection token",
            inline=False
        )
        embed.set_footer(text="⚡ MINNAL Bot - Admin Panel")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(WebBridgeCog(bot))