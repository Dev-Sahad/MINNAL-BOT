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
import logger as log
from gtts import gTTS

FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
FFMPEG_OPTIONS = {'options': '-vn'}
SETTINGS_FILE = "data/settings.json"
AUDIO_DIR = "audio"


def load_voices():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('voices', {}).get('voice_list', [])
    except Exception as e:
        log.error("voices", str(e))
    return []


def get_default_spells():
    return [
        {"spell": "Domain Expansion!", "anime": "Sukuna - JJK", "voice_text": "Domain Expansion!", "audio_file": "sukuna.mp3"},
        {"spell": "Unlimited Void!", "anime": "Gojo - JJK", "voice_text": "Unlimited Void!", "audio_file": "gojo.mp3"},
        {"spell": "Rasengan!", "anime": "Naruto", "voice_text": "Rasengan!", "audio_file": "naruto_rasengan.mp3"},
        {"spell": "Chidori!", "anime": "Sasuke", "voice_text": "Chidori!", "audio_file": "sasuke_chidori.mp3"},
        {"spell": "Kamehameha!", "anime": "Goku", "voice_text": "Kamehameha!", "audio_file": "goku_kamehameha.mp3"}
    ]


class VoiceFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processed_users = set()
        self.tts_dir = "tts_cache"
        os.makedirs(self.tts_dir, exist_ok=True)
        os.makedirs(AUDIO_DIR, exist_ok=True)

    def get_spells(self):
        voices = load_voices()
        return voices if voices else get_default_spells()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or not after.channel:
            return
        if before.channel and before.channel.id == after.channel.id:
            return
        log.event("voices", f"{member.name} joined {after.channel.name}")
        await asyncio.sleep(2)
        guild = member.guild
        updated_member = guild.get_member(member.id)
        if not updated_member or not updated_member.voice:
            return
        current_channel = updated_member.voice.channel
        if not current_channel:
            return
        voice_manager = self.bot.get_cog('SummonDomain')
        if not voice_manager or current_channel.id not in voice_manager.active_domains:
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
            log.event("voices", f"Casting: {spell_data['spell']}")
            try:
                guild = channel.guild
                notif_channel = guild.system_channel or discord.utils.find(lambda c: c.permissions_for(guild.me).send_messages, guild.text_channels)
                if notif_channel:
                    embed = discord.Embed(title="⚡ ANIME SPELL CAST!", description=f"**{spell_data['spell']}**", color=discord.Color.purple())
                    embed.add_field(name="🎭 From", value=spell_data['anime'], inline=True)
                    embed.add_field(name="👤 Cast on", value=member.mention, inline=True)
                    if spell_data.get('audio_file'):
                        embed.add_field(name="🎤 Voice", value="Real anime audio!", inline=True)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await notif_channel.send(embed=embed, delete_after=20)
            except Exception as e:
                log.warn("voices", f"Notification error: {e}")

            audio_filename = spell_data.get('audio_file', '').strip()
            if audio_filename:
                audio_path = os.path.join(AUDIO_DIR, audio_filename)
                if os.path.exists(audio_path):
                    audio_file = audio_path
                    is_temp_file = False
                else:
                    audio_file = await self.generate_tts(spell_data['voice_text'])
                    is_temp_file = True
            else:
                audio_file = await self.generate_tts(spell_data['voice_text'])
                is_temp_file = True

            if not audio_file:
                return

            existing_vc = channel.guild.voice_client
            if existing_vc:
                await existing_vc.move_to(channel)
                voice_client = existing_vc
            else:
                voice_client = await channel.connect()

            audio_source = discord.FFmpegPCMAudio(audio_file, executable=FFMPEG_PATH, **FFMPEG_OPTIONS)
            voice_client.play(audio_source)
            while voice_client.is_playing():
                await asyncio.sleep(0.5)
            await asyncio.sleep(1)
            await voice_client.disconnect()
        except Exception as e:
            log.error("voices", f"Cast error: {e}")
            try:
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
            except Exception:
                pass
        finally:
            if is_temp_file and audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except Exception:
                    pass

    async def generate_tts(self, text):
        try:
            filename = os.path.join(self.tts_dir, f"spell_{random.randint(1000, 9999)}.mp3")
            await asyncio.get_event_loop().run_in_executor(None, lambda: gTTS(text=text, lang='en', slow=False).save(filename))
            return filename
        except Exception as e:
            log.error("voices", f"TTS error: {e}")
            return None

    @app_commands.command(name="listvoices", description="🎤 List available anime voices")
    async def list_voices(self, interaction: discord.Interaction):
        spells = self.get_spells()
        embed = discord.Embed(title="🎤 Available Anime Voices", description=f"Total: **{len(spells)}** voices", color=discord.Color.purple())
        for spell in spells[:25]:
            audio_status = "🎤 Real Voice" if spell.get('audio_file') else "🔊 TTS"
            embed.add_field(name=f"{spell['spell']} ({audio_status})", value=f"From: {spell['anime']}", inline=False)
        embed.set_footer(text="Edit voices in data/settings.json → voices.voice_list")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(VoiceFeatures(bot))