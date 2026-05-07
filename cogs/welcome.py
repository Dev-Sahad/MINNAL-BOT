import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import json
import os

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/settings.json"
        self.assets_path = "assets"
        self.banner_path = f"{self.assets_path}/welcome_banner.png"
        self.font_path = f"{self.assets_path}/Ginto-Nord-700.ttf"

    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('welcome', {})
        except Exception as e:
            print(f"⚠️ Config Load Error: {e}")
        return {}

    def hex_to_rgb(self, hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    async def create_welcome_image(self, member):
        try:
            conf = self.load_settings()
            if not os.path.exists(self.banner_path):
                return None

            base = Image.open(self.banner_path).convert('RGBA')

            async with aiohttp.ClientSession() as session:
                async with session.get(str(member.display_avatar.url)) as resp:
                    if resp.status != 200: return None
                    avatar_bytes = await resp.read()

            avatar_size = conf.get('avatar_size', 145)
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA').resize((avatar_size, avatar_size))

            mask = Image.new('L', (avatar_size, avatar_size), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, avatar_size, avatar_size], fill=255)
            avatar.putalpha(mask)

            ax, ay = conf.get('avatar_x', 25), conf.get('avatar_y', 35)
            base.paste(avatar, (int(ax), int(ay)), avatar)

            ux, uy = conf.get('username_x', 25), conf.get('username_y', 205)
            u_size = conf.get('username_size', 32)
            u_color = self.hex_to_rgb(conf.get('username_color', '#FFFFFF'))

            try:
                font = ImageFont.truetype(self.font_path, u_size) if os.path.exists(self.font_path) else ImageFont.load_default()
            except:
                font = ImageFont.load_default()

            ImageDraw.Draw(base).text((int(ux), int(uy)), f"{member.name.upper()}", fill=u_color + (255,), font=font)

            out = io.BytesIO()
            base.convert('RGB').save(out, format='PNG', quality=95)
            out.seek(0)
            return discord.File(out, filename="welcome.png")
        except Exception as e:
            print(f"❌ Image Creation Failed: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conf = self.load_settings()
        if not conf.get('enabled', True): return

        channel_id = None
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)
                    channel_conf = full_config.get('channels', {})
                    channel_id = channel_conf.get('welcome_channel_id')
        except Exception as e:
            print(f"⚠️ Config Load Error for welcome channel: {e}")
            return

        if not channel_id:
            print("⚠️ Welcome channel ID not found in settings.json under 'channels'.")
            return

        channel = self.bot.get_channel(int(channel_id))
        if not channel: return

        img = await self.create_welcome_image(member)

        # --- Custom Welcome Protocol Message ---
        welcome_text = (
            f"**`|`** 👋 **IDENTITY:** {member.mention}\n"
            f"**`|`** 📑 **REGISTRY:** `Member #{len(member.guild.members)}`\n"
            f"**`|`** 📡 **LOCATION:** `{member.guild.name}`\n"
            f"**`#———————————————————————————————#`**\n\n"
            f"**`|`** 📜 **CORE PROTOCOLS:**\n"
            f"**`|`** 1️⃣ Respect the ` Community `.\n"
            f"**`|`** 2️⃣ Stay active and have ` Fun `.\n"
            f"**`|`** 3️⃣ Enjoy your ` Stay `\n\n"
            f"**`#———————————————————————————————#`**\n"
            f"**` STATUS: ACCESS GRANTED `**"
        )

        embed = discord.Embed(
            title=f"WELCOME TO THE {member.guild.name.upper()}",
            description=welcome_text,
            color=0x9400D3
        )

        if img:
            embed.set_image(url="attachment://welcome.png")
            await channel.send(embed=embed, file=img)
        else:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        welcome_conf = self.load_settings()
        if not welcome_conf.get('enabled', True):
            return

        channel_id = None
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)
                    channel_conf = full_config.get('channels', {})
                    channel_id = channel_conf.get('leave_channel_id')
        except Exception as e:
            print(f"⚠️ Config Load Error for leave channel: {e}")
            return

        if not channel_id:
            print("⚠️ Leave channel ID not found in settings.json under 'channels'.")
            return

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            print(f"⚠️ Could not find leave channel with ID: {channel_id}")
            return

        embed = discord.Embed(
            title=f"GOODBYE, {member.name.upper()}!",
            description=f"**`|`** 👋 **DEPARTURE:** {member.mention}\n"
                        f"**`|`** 📡 **LOCATION:** `{member.guild.name}`\n"
                        f"**`#———————————————————————————————#`**\n\n"
                        f"**` STATUS: CONNECTION TERMINATED `**",
            color=0xFF0000  # Red
        )

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
