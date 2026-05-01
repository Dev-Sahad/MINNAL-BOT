# =============================================================================
#  cogs/voice_features.py — Anime Voice System (with audio files + TTS fallback)
# =============================================================================

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import os
import json
import shutil
from gtts import gTTS

FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
print(f"🎵 voice_features.py - FFmpeg: {FFMPEG_PATH}", flush=True)

FFMPEG_OPTIONS = {'options': '-vn'}

# Settings file path
SETTINGS_FILE = "data/settings.json"
AUDIO_DIR = "audio"


def load_voices():
    """Load voice mappings from settings.json"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('voices', {}).get('voice_list', [])
    except Exception as e:
        print(f"❌ Voices load error: {e}", flush=True)
    return []


def get_default_spells():
    """Default spells if voices not set"""
    return [
        {"spell": "Domain Expansion!", "anime": "Sukuna - JJK", "voice_text": "Domain Expansion!", "audio_file": ""},
        {"spell": "Unlimited Void!", "anime": "Gojo - JJK", "voice_text": "Unlimited Void!", "audio_file": ""},
        {"spell": "Rasengan!", "anime": "Naruto", "voice_text": "Rasengan!", "audio_file": ""},
        {"spell": "Chidori!", "anime": "Sasuke", "voice_text": "Chidori!", "audio_file": ""},
        {"spell": "Kamehameha!", "anime": "Goku", "voice_text": "Kamehameha!", "audio_file": ""}
    ]


class VoiceFeatures(commands.Cog):
    """Anime Voice System with audio file support"""
    
    def __init__(self, bot):
        self.bot = bot
        self.processed_users = set()
        self.tts_dir = "tts_cache"
        if not os.path.exists(self.tts_dir):
            os.makedirs(self.tts_dir)
        if not os.path.exists(AUDIO_DIR):
            os.makedirs(AUDIO_DIR)
        print("✅ VoiceFeatures cog initialized!", flush=True)
    
    def get_spells(self):
        """Get spells from settings or defaults"""
        voices = load_voices()
        if voices:
            return voices
        return get_default_spells()
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        
        if not after.channel:
            return
        
        if before.channel and before.channel.id == after.channel.id:
            return
        
        print(f"🔔 {member.name} joined {after.channel.name}", flush=True)
        await asyncio.sleep(2)
        
        guild = member.guild
        updated_member = guild.get_member(member.id)
        
        if not updated_member or not updated_member.voice:
            return
        
        current_channel = updated_member.voice.channel
        if not current_channel:
            return
        
        voice_manager = self.bot.get_cog('SummonDomain')
        if not voice_manager:
            return
        
        if current_channel.id not in voice_manager.active_domains:
            return
        
        user_key = f"{member.id}_{current_channel.id}"
        if user_key in self.processed_users:
            return
        
        self.processed_users.add(user_key)
        await self.cast_spell(current_channel, updated_member)
        await asyncio.sleep(60)
        self.processed_users.discard(user_key)
    
    async def cast_spell(self, channel, member):
        voice_client = None
        audio_file = None
        is_temp_file = False
        
        try:
            spells = self.get_spells()
            spell_data = random.choice(spells)
            print(f"⚡ Casting: {spell_data['spell']}", flush=True)
            
            # Send notification
            try:
                guild = channel.guild
                notif_channel = guild.system_channel
                if not notif_channel:
                    notif_channel = discord.utils.find(
                        lambda c: c.permissions_for(guild.me).send_messages,
                        guild.text_channels
                    )
                
                if notif_channel:
                    embed = discord.Embed(
                        title="⚡ ANIME SPELL CAST!",
                        description=f"**{spell_data['spell']}**",
                        color=discord.Color.purple()
                    )
                    embed.add_field(name="🎭 From", value=spell_data['anime'], inline=True)
                    embed.add_field(name="👤 Cast on", value=member.mention, inline=True)
                    if spell_data.get('audio_file'):
                        embed.add_field(name="🎤 Voice", value="Real anime audio!", inline=True)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await notif_channel.send(embed=embed, delete_after=20)
            except Exception as e:
                print(f"Notification error: {e}", flush=True)
            
            # Try to use audio file first
            audio_filename = spell_data.get('audio_file', '').strip()
            
            if audio_filename:
                # Use audio file
                audio_path = os.path.join(AUDIO_DIR, audio_filename)
                if os.path.exists(audio_path):
                    audio_file = audio_path
                    is_temp_file = False
                    print(f"🎤 Using audio file: {audio_filename}", flush=True)
                else:
                    print(f"⚠️ Audio file not found: {audio_path}, falling back to TTS", flush=True)
                    audio_file = await self.generate_tts(spell_data['voice_text'])
                    is_temp_file = True
            else:
                # Use TTS
                print(f"🔊 Using TTS for: {spell_data['voice_text']}", flush=True)
                audio_file = await self.generate_tts(spell_data['voice_text'])
                is_temp_file = True
            
            if not audio_file:
                print("❌ No audio available!", flush=True)
                return
            
            # Connect to voice channel
            existing_vc = channel.guild.voice_client
            if existing_vc:
                await existing_vc.move_to(channel)
                voice_client = existing_vc
            else:
                voice_client = await channel.connect()
            
            print("✅ Connected!", flush=True)
            
            # Play audio
            audio_source = discord.FFmpegPCMAudio(
                audio_file,
                executable=FFMPEG_PATH,
                **FFMPEG_OPTIONS
            )
            
            voice_client.play(audio_source)
            print("🎵 Playing...", flush=True)
            
            # Wait for finish
            timeout = 0
            while voice_client.is_playing() and timeout < 30:
                await asyncio.sleep(0.5)
                timeout += 1
            
            await asyncio.sleep(1)
            await voice_client.disconnect()
            print("👋 Disconnected", flush=True)
        
        except Exception as e:
            print(f"❌ Cast error: {e}", flush=True)
            try:
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
            except Exception:
                pass
        
        finally:
            # Only cleanup TTS temp files, NOT audio files in audio/ folder
            if is_temp_file and audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except Exception:
                    pass
    
    async def generate_tts(self, text):
        try:
            filename = os.path.join(self.tts_dir, f"spell_{random.randint(1000, 9999)}.mp3")
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: gTTS(text=text, lang='en', slow=False).save(filename)
            )
            return filename
        except Exception as e:
            print(f"❌ TTS error: {e}", flush=True)
            return None
    
    @app_commands.command(name="say", description="🗣️ Make bot speak in voice channel")
    @app_commands.describe(message="The message to speak")
    async def say_slash(self, interaction: discord.Interaction, message: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Join a voice channel!", ephemeral=True)
            return
        
        if len(message) > 200:
            await interaction.response.send_message("❌ Max 200 chars!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        
        if voice_client:
            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
            if voice_client.is_playing():
                await interaction.followup.send("❌ Already playing!")
                return
        else:
            try:
                voice_client = await voice_channel.connect()
            except Exception as e:
                await interaction.followup.send(f"❌ Could not connect: {e}")
                return
        
        embed = discord.Embed(
            title="🗣️ Speaking...",
            description=f"**{message}**",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)
        
        audio_file = await self.generate_tts(message)
        
        if audio_file:
            try:
                audio_source = discord.FFmpegPCMAudio(
                    audio_file,
                    executable=FFMPEG_PATH,
                    **FFMPEG_OPTIONS
                )
                voice_client.play(audio_source)
                
                while voice_client.is_playing():
                    await asyncio.sleep(0.5)
                
                try:
                    os.remove(audio_file)
                except Exception:
                    pass
            except Exception as e:
                print(f"TTS error: {e}", flush=True)
    
    @app_commands.command(name="spell", description="⚡ Cast a random anime spell")
    async def spell_slash(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Join a voice channel!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        spells = self.get_spells()
        spell_data = random.choice(spells)
        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        
        if voice_client:
            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
            if voice_client.is_playing():
                await interaction.followup.send("❌ Already playing!")
                return
        else:
            try:
                voice_client = await voice_channel.connect()
            except Exception as e:
                await interaction.followup.send(f"❌ Could not connect: {e}")
                return
        
        embed = discord.Embed(
            title="⚡ ANIME SPELL!",
            description=f"**{spell_data['spell']}**",
            color=discord.Color.purple()
        )
        embed.add_field(name="🎭 From", value=spell_data['anime'])
        await interaction.followup.send(embed=embed)
        
        # Get audio
        audio_filename = spell_data.get('audio_file', '').strip()
        audio_file = None
        is_temp = False
        
        if audio_filename:
            path = os.path.join(AUDIO_DIR, audio_filename)
            if os.path.exists(path):
                audio_file = path
        
        if not audio_file:
            audio_file = await self.generate_tts(spell_data['voice_text'])
            is_temp = True
        
        if audio_file:
            try:
                audio_source = discord.FFmpegPCMAudio(
                    audio_file,
                    executable=FFMPEG_PATH,
                    **FFMPEG_OPTIONS
                )
                voice_client.play(audio_source)
                
                while voice_client.is_playing():
                    await asyncio.sleep(0.5)
                
                if is_temp:
                    try:
                        os.remove(audio_file)
                    except Exception:
                        pass
            except Exception as e:
                print(f"Spell error: {e}", flush=True)
    
    @app_commands.command(name="listvoices", description="🎤 List available anime voices")
    async def list_voices(self, interaction: discord.Interaction):
        spells = self.get_spells()
        
        embed = discord.Embed(
            title="🎤 Available Anime Voices",
            description=f"Total: **{len(spells)}** voices",
            color=discord.Color.purple()
        )
        
        for spell in spells[:25]:  # Discord embed limit
            audio_status = "🎤 Real Voice" if spell.get('audio_file') else "🔊 TTS"
            embed.add_field(
                name=f"{spell['spell']} ({audio_status})",
                value=f"From: {spell['anime']}",
                inline=False
            )
        
        embed.set_footer(text="Edit voices in admin panel: minnal.up.railway.app")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(VoiceFeatures(bot))
    print("✅ VoiceFeatures cog loaded!", flush=True)
