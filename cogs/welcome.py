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
        self.banner_path = "assets/welcome_banner.png"

    def load_settings(self):
        """Load latest settings from JSON."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('welcome', {})
        except Exception as e:
            print(f"⚠️ Config Load Error: {e}")
        return {}

    def hex_to_rgb(self, hex_str):
        """Converts #RRGGBB to (R, G, B) tuple."""
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    async def create_welcome_image(self, member):
        """Generates dynamic image based on settings.json positions."""
        try:
            conf = self.load_settings()
            if not os.path.exists(self.banner_path):
                return None

            # 1. Base Image
            base = Image.open(self.banner_path).convert('RGBA')
            w, h = base.size

            # 2. Get Avatar
            async with aiohttp.ClientSession() as session:
                async with session.get(str(member.display_avatar.url)) as resp:
                    avatar_bytes = await resp.read()
            
            size = conf.get('avatar_size', 180)
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA').resize((size, size))

            # 3. Apply Circular Mask
            mask = Image.new('L', (size, size), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
            avatar.putalpha(mask)

            # 4. Handle Border
            if conf.get('avatar_border', True):
                bw = conf.get('border_width', 5)
                bc = self.hex_to_rgb(conf.get('border_color', '#9400D3'))
                
                canvas_size = size + (bw * 2)
                bordered = Image.new('RGBA', (canvas_size, canvas_size), (0,0,0,0))
                draw_b = ImageDraw.Draw(bordered)
                draw_b.ellipse([0, 0, canvas_size, canvas_size], outline=bc + (255,), width=bw)
                bordered.paste(avatar, (bw, bw), avatar)
                avatar = bordered
                size = canvas_size # Update size for positioning

            # 5. Positioning Logic (Defaults to right-center if null)
            ax = conf.get('avatar_x') if conf.get('avatar_x') is not None else (w - size - 40)
            ay = conf.get('avatar_y') if conf.get('avatar_y') is not None else (h - size) // 2
            base.paste(avatar, (int(ax), int(ay)), avatar)

            # 6. Username Text
            ux = conf.get('username_x', 50)
            uy = conf.get('username_y', h - 100)
            u_size = conf.get('username_size', 50)
            u_color = self.hex_to_rgb(conf.get('username_color', '#FFFFFF'))

            try:
                # Ensure path matches your server's font location
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", u_size)
            except:
                font = ImageFont.load_default()

            ImageDraw.Draw(base).text((int(ux), int(uy)), f"@{member.name}", fill=u_color + (255,), font=font)

            # 7. Finalize
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
        
        channel = self.bot.get_channel(int(conf.get('channel_id')))
        if not channel: return

        img = await self.create_welcome_image(member)
        embed = discord.Embed(title="🎉 Welcome!", color=0x9400D3)
        embed.set_image(url="attachment://welcome.png")
        
        await channel.send(content=f"Welcome {member.mention}!", embed=embed, file=img)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
