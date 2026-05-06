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
        """Load settings for positioning and colors."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('welcome', {})
        except Exception as e:
            print(f"⚠️ Config Load Error: {e}")
        return {}

    def hex_to_rgb(self, hex_str):
        """Converts hex color codes to RGB tuples."""
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    async def create_welcome_image(self, member):
        """Generates the welcome banner with dynamic member data."""
        try:
            conf = self.load_settings()
            if not os.path.exists(self.banner_path):
                print(f"❌ Error: Banner not found at {self.banner_path}")
                return None

            # 1. Load Background
            base = Image.open(self.banner_path).convert('RGBA')
            w, h = base.size

            # 2. Fetch Member Avatar
            async with aiohttp.ClientSession() as session:
                async with session.get(str(member.display_avatar.url)) as resp:
                    if resp.status != 200:
                        return None
                    avatar_bytes = await resp.read()
            
            # 145px matches the demo circle size
            avatar_size = conf.get('avatar_size', 145) 
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA').resize((avatar_size, avatar_size))

            # 3. Create Circular Mask for Avatar
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse([0, 0, avatar_size, avatar_size], fill=255)
            avatar.putalpha(mask)

            # 4. Position Avatar (Aligned to the left circle in your template)
            ax = conf.get('avatar_x', 25) 
            ay = conf.get('avatar_y', 35)
            base.paste(avatar, (int(ax), int(ay)), avatar)

            # 5. Handle Username with Ginto Nord 700
            ux = conf.get('username_x', 25)
            uy = conf.get('username_y', 205) # Positioned below avatar
            u_size = conf.get('username_size', 32)
            u_color = self.hex_to_rgb(conf.get('username_color', '#FFFFFF'))

            try:
                if os.path.exists(self.font_path):
                    font = ImageFont.truetype(self.font_path, u_size)
                else:
                    # Fallback for Linux environments
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", u_size)
            except:
                font = ImageFont.load_default()

            # Draw text in UPPERCASE to match mockup style
            draw = ImageDraw.Draw(base)
            draw.text((int(ux), int(uy)), f"{member.name.upper()}", fill=u_color + (255,), font=font)

            # 6. Save to Buffer
            out = io.BytesIO()
            base.convert('RGB').save(out, format='PNG', quality=95)
            out.seek(0)
            return discord.File(out, filename="welcome.png")

        except Exception as e:
            print(f"❌ Image Creation Failed: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Triggers when a member joins the server."""
        conf = self.load_settings()
        if not conf.get('enabled', True):
            return
        
        channel_id = conf.get('channel_id')
        if not channel_id:
            return

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            return

        img = await self.create_welcome_image(member)
        if not img:
            return

        # Create the embed for the welcome message
        embed = discord.Embed(
            title="🎉 New Member Arrived!",
            description=f"**WELCOME TO THE {server}**",
    "message": "**`|`** 👋 **IDENTITY:** {member}\n**`|`** 📑 **REGISTRY:** `Member #{member guild.member_count}`\n**`|`** 📡 **LOCATION:** `{member guild.name}`\n**`#———————————————————————————————#`**\n\n**`|`** 📜 **CORE PROTOCOLS:**\n**`|`** 1️⃣ Respect the ` Community`.\n**`|`** 2️⃣ Stay active and have ` Fun `.\n**`|`** 3️⃣ Enjoy your ` Stay `\n\n**`#———————————————————————————————#`**\n**` STATUS: ACCESS GRANTED `**",
    "avatar_x": 25,
    "avatar_y": 35,
    "avatar_size": 180,
    "avatar_border": true,
    "border_color": "#9400D3",
    "border_width": 5,
    "username_x": 25,
    "username_y": 205,
    "username_size": 32,
    "username_color": "#FFFFFF",
            color=0x9400D3
        )
        embed.set_image(url="attachment://welcome.png")
        
        await channel.send(embed=embed, file=img)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
        
