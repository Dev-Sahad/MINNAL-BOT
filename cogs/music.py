# =============================================================================
#  cogs/music.py — SoundCloud Music Player (with FFmpeg path fix)
# =============================================================================

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp
import shutil
import os
from collections import deque


# Find FFmpeg location
FFMPEG_PATH = shutil.which("ffmpeg")
if not FFMPEG_PATH:
    # Try common locations
    for path in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/nix/store/ffmpeg"]:
        if os.path.exists(path):
            FFMPEG_PATH = path
            break
    if not FFMPEG_PATH:
        FFMPEG_PATH = "ffmpeg"  # Use PATH fallback

# FFmpeg ready — path logged at startup by discord_bot.py

# yt-dlp options for SoundCloud
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'scsearch',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class Song:
    def __init__(self, source, title, url, requester, duration=0):
        self.source = source
        self.title = title
        self.url = url
        self.requester = requester
        self.duration = duration


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.now_playing = {}
    
    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]
    
    async def search_song(self, query):
        """Search SoundCloud for a song"""
        try:
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(query, download=False)
                )
                
                if 'entries' in info:
                    info = info['entries'][0]
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'url': info.get('url', ''),
                    'webpage_url': info.get('webpage_url', ''),
                    'duration': info.get('duration', 0)
                }
        except Exception as e:
            print(f"Search error: {e}", flush=True)
            return None
    
    async def play_next(self, interaction):
        """Play next song in queue"""
        guild_id = interaction.guild.id
        queue = self.get_queue(guild_id)
        
        if not queue:
            self.now_playing[guild_id] = None
            return
        
        voice_client = interaction.guild.voice_client
        if not voice_client:
            return
        
        song = queue.popleft()
        self.now_playing[guild_id] = song
        
        try:
            # Use FFMPEG_PATH explicitly!
            source = discord.FFmpegPCMAudio(
                song.url,
                executable=FFMPEG_PATH,
                **FFMPEG_OPTIONS
            )
            
            voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(interaction), self.bot.loop
                ).result() if e is None else print(f"Player error: {e}", flush=True)
            )
            
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"**{song.title}**",
                color=discord.Color.purple()
            )
            embed.add_field(name="Requested by", value=song.requester.mention)
            try:
                await interaction.channel.send(embed=embed)
            except:
                pass
        except Exception as e:
            print(f"Playback error: {e}", flush=True)
    
    @app_commands.command(name="play", description="🎵 Play music from SoundCloud")
    @app_commands.describe(query="Song name or URL")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        
        if not interaction.user.voice:
            await interaction.followup.send("❌ Join a voice channel first!", ephemeral=True)
            return
        
        voice_channel = interaction.user.voice.channel
        
        # Connect or move to channel
        if not interaction.guild.voice_client:
            try:
                await voice_channel.connect()
            except Exception as e:
                await interaction.followup.send(f"❌ Could not connect: {e}", ephemeral=True)
                return
        else:
            if interaction.guild.voice_client.channel != voice_channel:
                await interaction.guild.voice_client.move_to(voice_channel)
        
        await interaction.followup.send(f"🔍 Searching SoundCloud: **{query}**...")
        
        song_info = await self.search_song(query)
        
        if not song_info:
            await interaction.followup.send("❌ Song not found!")
            return
        
        song = Song(
            source=song_info['url'],
            title=song_info['title'],
            url=song_info['url'],
            requester=interaction.user,
            duration=song_info['duration']
        )
        
        queue = self.get_queue(interaction.guild.id)
        queue.append(song)
        
        embed = discord.Embed(
            title="✅ Added to Queue",
            description=f"**{song.title}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Position", value=f"#{len(queue)}", inline=True)
        embed.add_field(name="Requested by", value=interaction.user.mention, inline=True)
        embed.set_footer(text="Source: SoundCloud")
        
        await interaction.followup.send(embed=embed)
        
        if not interaction.guild.voice_client.is_playing():
            await self.play_next(interaction)
    
    @app_commands.command(name="skip", description="⏭️ Skip current song")
    async def skip(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        if not interaction.guild.voice_client.is_playing():
            await interaction.response.send_message("❌ Nothing playing!", ephemeral=True)
            return
        
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped!")
    
    @app_commands.command(name="queue", description="📋 Show music queue")
    async def show_queue(self, interaction: discord.Interaction):
        queue = self.get_queue(interaction.guild.id)
        now_playing = self.now_playing.get(interaction.guild.id)
        
        embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.purple())
        
        if now_playing:
            embed.add_field(
                name="🎶 Now Playing",
                value=f"**{now_playing.title}**",
                inline=False
            )
        
        if not queue:
            embed.description = "Queue is empty!"
        else:
            queue_text = "\n".join([f"{i+1}. **{s.title}**" for i, s in enumerate(list(queue)[:10])])
            embed.add_field(name="📋 Up Next", value=queue_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pause", description="⏸️ Pause music")
    async def pause(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("⏸️ Paused")
        else:
            await interaction.response.send_message("❌ Nothing playing!", ephemeral=True)
    
    @app_commands.command(name="resume", description="▶️ Resume music")
    async def resume(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        if interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("▶️ Resumed")
        else:
            await interaction.response.send_message("❌ Nothing paused!", ephemeral=True)
    
    @app_commands.command(name="stop", description="⏹️ Stop and disconnect")
    async def stop(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        self.queues[interaction.guild.id] = deque()
        self.now_playing[interaction.guild.id] = None
        
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Stopped")
    
    @app_commands.command(name="join", description="🔊 Join your voice channel")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Join a VC first!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect()
        
        await interaction.response.send_message(f"✅ Joined {channel.mention}")
    
    @app_commands.command(name="leave", description="👋 Leave voice channel")
    async def leave(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Not in VC!", ephemeral=True)
            return
        
        await interaction.guild.voice_client.disconnect()
        self.queues[interaction.guild.id] = deque()
        self.now_playing[interaction.guild.id] = None
        await interaction.response.send_message("👋 Left voice channel")
    
    @app_commands.command(name="nowplaying", description="🎶 Show current song")
    async def nowplaying(self, interaction: discord.Interaction):
        now_playing = self.now_playing.get(interaction.guild.id)
        
        if not now_playing:
            await interaction.response.send_message("❌ Nothing playing!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"**{now_playing.title}**",
            color=discord.Color.purple()
        )
        embed.add_field(name="Requested by", value=now_playing.requester.mention)
        await interaction.response.send_message(embed=embed)
    
    async def update_presence(self):
        pass


async def setup(bot):
    await bot.add_cog(MusicCog(bot)) 
