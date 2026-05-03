# =============================================================================
#  cogs/welcome.py — Welcome System with CUSTOMIZABLE Positions
# =============================================================================

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
        
        # ═══════════════════════════════════════════════════════════════════
        # 🎨 CUSTOMIZE THESE VALUES TO CHANGE POSITIONS AND SIZES! 🎨
        # ═══════════════════════════════════════════════════════════════════
        
        # Avatar size (in pixels) - make it bigger/smaller
        self.AVATAR_SIZE = 180  # Change this: 100-250 recommended
        
        # Avatar X position (from left edge)
        self.AVATAR_X = None  # None = right edge. Or set: 50, 100, 200, etc
        
        # Avatar Y position (from top edge)
        self.AVATAR_Y = None  # None = center vertically. Or set: 50, 100, 200, etc
        
        # Username text X position
        self.USERNAME_X = 50  # From left edge - change for left/right
        
        # Username text Y position
        self.USERNAME_Y = None  # None = auto. Or set: 100, 200, 300, etc
        
        # Username text size (font size in pixels)
        self.USERNAME_SIZE = 50  # Bigger = larger text (30-80 recommended)
        
        # Username color (RGB)
        self.USERNAME_COLOR = (255, 255, 255)  # White (R, G, B) 0-255
        
        # Add border/glow around avatar? True/False
        self.AVATAR_BORDER = True
        
        # Border color (RGB)
        self.BORDER_COLOR = (148, 0, 211)  # Purple (matches your theme!)
        
        # Border width (pixels)
        self.BORDER_WIDTH = 5  # Change: 2-10 recommended
        
        # ═══════════════════════════════════════════════════════════════════

    def load_settings(self):
        """Load welcome settings from config"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('welcome', {})
        except:
            pass
        return {}

    async def create_welcome_image(self, member):
        """Create personalized welcome image with member avatar overlay"""
        try:
            # Check if banner exists
            if not os.path.exists(self.banner_path):
                print(f"⚠️ Banner not found at {self.banner_path}", flush=True)
                return None
            
            # Open the base banner
            base_image = Image.open(self.banner_path).convert('RGBA')
            width, height = base_image.size
            
            # Get member avatar
            async with aiohttp.ClientSession() as session:
                async with session.get(str(member.display_avatar.url)) as resp:
                    avatar_data = await resp.read()
            
            avatar_img = Image.open(io.BytesIO(avatar_data)).convert('RGBA')
            avatar_img = avatar_img.resize((self.AVATAR_SIZE, self.AVATAR_SIZE))
            
            # Create circular mask
            mask = Image.new('L', (self.AVATAR_SIZE, self.AVATAR_SIZE), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([0, 0, self.AVATAR_SIZE, self.AVATAR_SIZE], fill=255)
            avatar_img.putalpha(mask)
            
            # Add border if enabled
            if self.AVATAR_BORDER:
                # Create border image
                bordered = Image.new('RGBA', 
                    (self.AVATAR_SIZE + self.BORDER_WIDTH * 2, 
                     self.AVATAR_SIZE + self.BORDER_WIDTH * 2), 
                    (0, 0, 0, 0))
                
                # Draw circle border
                border_draw = ImageDraw.Draw(bordered)
                border_draw.ellipse(
                    [0, 0, 
                     self.AVATAR_SIZE + self.BORDER_WIDTH * 2, 
                     self.AVATAR_SIZE + self.BORDER_WIDTH * 2],
                    outline=self.BORDER_COLOR + (255,),
                    width=self.BORDER_WIDTH
                )
                
                # Paste avatar in center
                bordered.paste(avatar_img, 
                    (self.BORDER_WIDTH, self.BORDER_WIDTH), 
                    avatar_img)
                
                avatar_img = bordered
                avatar_size_with_border = self.AVATAR_SIZE + self.BORDER_WIDTH * 2
            else:
                avatar_size_with_border = self.AVATAR_SIZE
            
            # Calculate avatar position
            if self.AVATAR_X is None:
                # Right side (default)
                avatar_x = width - avatar_size_with_border - 40
            else:
                avatar_x = self.AVATAR_X
            
            if self.AVATAR_Y is None:
                # Center vertically (default)
                avatar_y = (height - avatar_size_with_border) // 2
            else:
                avatar_y = self.AVATAR_Y
            
            # Paste avatar
            base_image.paste(avatar_img, (avatar_x, avatar_y), avatar_img)
            
            # Add member name text
            try:
                title_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
                    self.USERNAME_SIZE)
            except:
                title_font = ImageFont.load_default()
            
            draw = ImageDraw.Draw(base_image)
            
            # Calculate username position
            member_name = f"@{member.name}"
            
            if self.USERNAME_Y is None:
                # Auto position at bottom
                username_y = height - 80
            else:
                username_y = self.USERNAME_Y
            
            # Draw member name
            draw.text(
                (self.USERNAME_X, username_y), 
                member_name, 
                fill=self.USERNAME_COLOR + (255,), 
                font=title_font)
            
            # Convert to RGB for Discord
            base_image = base_image.convert('RGB')
            
            # Save to bytes
            img_bytes = io.BytesIO()
            base_image.save(img_bytes, format='PNG', quality=95)
            img_bytes.seek(0)
            
            return discord.File(img_bytes, filename="welcome.png")
            
        except Exception as e:
            print(f"❌ Image creation error: {e}", flush=True)
            return None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome new members with personalized banner"""
        settings = self.load_settings()
        
        if not settings.get('enabled', True):
            return
        
        channel_id = settings.get('channel_id')
        if not channel_id:
            print(f"⚠️ No welcome channel configured", flush=True)
            return
        
        try:
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                print(f"❌ Welcome channel {channel_id} not found", flush=True)
                return
            
            # Create welcome embed
            embed = discord.Embed(
                title="🎉 Welcome!",
                description=f"Welcome to **Sahad Is Live**, {member.mention}! 🌟",
                color=0x9400D3
            )
            
            tag = f"#{member.discriminator}" if member.discriminator != "0" else ""
            embed.set_author(
                name=f"{member.name}{tag}",
                icon_url=member.display_avatar.url
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            
            embed.add_field(name="Member #", value=f"{len(member.guild.members)}", inline=True)
            embed.add_field(name="Account Age", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
            
            embed.set_footer(text=f"ID: {member.id} | Welcome to the community!")
            
            # Create personalized image
            image_file = await self.create_welcome_image(member)
            
            if image_file:
                embed.set_image(url="attachment://welcome.png")
                await channel.send(f"🎊 Welcome {member.mention}! 🎊", embed=embed, file=image_file)
            else:
                await channel.send(f"🎊 Welcome {member.mention}! 🎊", embed=embed)
            
            print(f"✅ Welcomed {member.name} to {member.guild.name}", flush=True)
            
        except Exception as e:
            print(f"❌ Welcome error: {e}", flush=True)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Say goodbye when member leaves"""
        settings = self.load_settings()
        
        if not settings.get('enabled', True):
            return
        
        channel_id = settings.get('channel_id')
        if not channel_id:
            return
        
        try:
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)
            
            if channel:
                embed = discord.Embed(
                    title="👋 Member Left",
                    description=f"{member.mention} has left **Sahad Is Live**.",
                    color=0xFF0000
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
                
                await channel.send(embed=embed)
                print(f"👋 {member.name} left {member.guild.name}", flush=True)
        except Exception as e:
            print(f"❌ Goodbye error: {e}", flush=True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def testwelcome(self, ctx, member: discord.Member = None):
        """Test welcome message (Admin only)"""
        target = member or ctx.author
        
        settings = self.load_settings()
        channel_id = settings.get('channel_id')
        
        if not channel_id:
            await ctx.send("❌ No welcome channel configured in admin panel!")
            return
        
        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            await ctx.send(f"❌ Welcome channel not found: {channel_id}")
            return
        
        embed = discord.Embed(
            title="🎉 Welcome!",
            description=f"Welcome to **Sahad Is Live**, {target.mention}! 🌟",
            color=0x9400D3
        )
        
        tag = f"#{target.discriminator}" if target.discriminator != "0" else ""
        embed.set_author(name=f"{target.name}{tag}", icon_url=target.display_avatar.url)
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Member #", value=f"{len(ctx.guild.members)}", inline=True)
        embed.add_field(name="Account Age", value=f"<t:{int(target.created_at.timestamp())}:R>", inline=True)
        embed.set_footer(text=f"ID: {target.id} | Welcome to the community!")
        
        image_file = await self.create_welcome_image(target)
        
        if image_file:
            embed.set_image(url="attachment://welcome.png")
            await channel.send(f"🎊 Welcome {target.mention}! 🎊", embed=embed, file=image_file)
        else:
            await channel.send(f"🎊 Welcome {target.mention}! 🎊", embed=embed)
        
        await ctx.send(f"✅ Test welcome sent for {target.mention}!")


async def setup(bot):
    await bot.add_cog(Welcome(bot))
      
