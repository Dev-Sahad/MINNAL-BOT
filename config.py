# =============================================================================
#  config.py — Bot-wide settings & shared mutable state
#  Edit this file to change defaults before starting the bot.
# =============================================================================

from collections import deque

# ── Developer ────────────────────────────────────────────────────────────────
DEVELOPER = "SAHAD SHA"
DEVELOPER_IDS: list[int] = [853166408212807701] 

# ── MINNAL Core Role & Staff IDs ──────────────────────────────────────────────
# Replace these with your actual Role IDs (Right-click role in Discord -> Copy ID)
VERIFIED_ROLE_ID        = 1463854523935359115   # Role given after clicking Verify
UNVERIFIED_ROLE_ID      = 1463855462712868948   # Role given immediately on join
STAFF_ROLE_ID           = 853166408212807701    # Admins/Sub-Admins who can manage tickets

# ── Default channel IDs ───────────────────────────────────────────────────────
WELCOME_CHANNEL_ID      = 1463854523935359115   
LEAVE_CHANNEL_ID        = 1463855462712868948   
GAME_UPDATE_CHANNEL_ID  = 1467730984723284141   
MUSIC_CHANNEL_ID        = 1463956357530124329   
TICKET_CHANNEL_ID       = 1463882710656221255   # Channel for support buttons

# Voice Channels
DEFAULT_VOICE_CHANNEL_ID      = None   
ANNOUNCEMENT_VOICE_CHANNEL_ID = 1465838079821484186   

# ── Images ───────────────────────────────────────────────────────────────────
# Replace None with "URL" if you want a custom aesthetic banner
WELCOME_IMAGE_URL       = None  
LEAVE_IMAGE_URL         = None                  

# ── Auto-DM on member join ────────────────────────────────────────────────────
DM_JOIN_ENABLED  = True
DM_JOIN_MESSAGE  = (
    "👋 Hey **{member}**, welcome to **{server}**!\n\n"
    "We're glad to have you here. Please visit <#1463882710656221255> to verify your account and join the fam! 🎉"
)

# ── Music shared state ────────────────────────────────────────────────────────
music_queues       = {}   # guild_id -> deque of track dicts
now_playing        = {}   # guild_id -> track dict
music_text_channels = {}  # guild_id -> TextChannel

# ── yt-dlp options ────────────────────────────────────────────────────────────
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'socket_timeout': 30,
    'skip_unavailable_fragments': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['web'],
            'player_skip': ['webpage', 'config', 'get_fmt_quality'],
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    },
    'geo_bypass': True,
    'geo_bypass_country': 'US',
    'cachedir': './.yt-dlp-cache',
}

# ── FFmpeg options ────────────────────────────────────────────────────────────
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -loglevel panic',
    'options': '-vn -q:a 9',
}
