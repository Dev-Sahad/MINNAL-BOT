# ⚡ MINNAL BOT - COMPLETE PACKAGE
## Everything You Need to Run Your Bot!

---

## 📦 **WHAT'S INCLUDED:**

### **1. Complete Bot Files**
```
MINNAL-BOT-ULTRA/
├── discord_bot.py          # Main bot file
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── Procfile               # For hosting
├── runtime.txt            # Python version
├── cogs/                  # All bot features
│   ├── admin.py          # Admin commands (17 commands)
│   ├── economy.py        # Economy & leveling (8 commands)
│   ├── giveaways.py      # Giveaways (3 commands)
│   ├── music.py          # Music player (10 commands)
│   ├── fun.py            # Fun commands (5 commands)
│   ├── utilities.py      # Utilities (5 commands)
│   ├── info.py           # Info panel
│   ├── web_bridge.py     # Web panel bridge (4 commands)
│   └── checks.py         # Permission checks
└── README_ULTRA.md       # Full documentation
```

### **2. Web Admin Panels**
- `advanced-admin-panel.html` - Full web control panel
- `config-editor.html` - Simple config editor
- `admin-panel.html` - Original panel

### **3. Documentation**
- `README_ULTRA.md` - Complete feature guide
- `INSTALLATION_GUIDE.md` - Setup instructions
- `CHANGELOG.md` - What's new
- `WEB_BRIDGE_GUIDE.md` - Web-bot connection guide
- `WEB_PANEL_ADDITIONS.html` - Code snippets

---

## 🚀 **QUICK START (3 METHODS):**

### **Method 1: Replit (Easiest - 10 minutes)**

1. **Go to replit.com**
2. **Sign up with email**
3. **Create Python Repl**
4. **Upload all files from MINNAL-BOT-ULTRA folder**
5. **Add Secret:**
   - Key: `DISCORD_BOT_TOKEN`
   - Value: Your bot token
6. **Create main.py:**
```python
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
os.system('python discord_bot.py')
```
7. **Click Run**
8. **Bot is online!**

**Keep it alive 24/7:**
- Go to uptimerobot.com
- Create monitor with your Replit URL
- Ping every 5 minutes

---

### **Method 2: PythonAnywhere (Free 24/7)**

1. **Go to pythonanywhere.com**
2. **Create free account**
3. **Upload all files from MINNAL-BOT-ULTRA**
4. **Open Bash console:**
```bash
cd minnal-bot
pip3 install --user -r requirements.txt
echo "DISCORD_BOT_TOKEN=your_token" > .env
```
5. **Create Always-On Task:**
   - Command: `python3 discord_bot.py`
6. **Done!**

---

### **Method 3: Your Computer (Testing)**

1. **Extract MINNAL-BOT-ULTRA folder**
2. **Open terminal/command prompt**
3. **Navigate to folder:**
```bash
cd path/to/MINNAL-BOT-ULTRA
```
4. **Install dependencies:**
```bash
pip install -r requirements.txt
```
5. **Create .env file:**
```
DISCORD_BOT_TOKEN=your_actual_token_here
```
6. **Run:**
```bash
python discord_bot.py
```

---

## 🌐 **WEB PANEL SETUP:**

### **Upload to Netlify:**

1. **Go to netlify.com**
2. **Sign up**
3. **Drag & drop:** `advanced-admin-panel.html`
4. **Your panel is live!**
5. **Default password:** `MINNAL@2025`

**Change password:**
- Edit line 870 in HTML file
- Change `const PASSWORD = "MINNAL@2025";`

---

## 🔗 **LINK WEB TO BOT:**

After bot is running:

1. **In Discord:** `/link`
2. **Copy server token**
3. **Open web panel**
4. **Paste token in "Bot Connection" tab**
5. **Connected!**

---

## 💬 **50+ COMMANDS INCLUDED:**

### **Admin (17):**
`/send`, `/embed`, `/announce`, `/post`, `/welcome`, `/leavechannel`, `/gamechannel`, `/setwelcomeimage`, `/setleaveimage`, `/setmusicchannel`, `/clearmusicchannel`, `/setdmmessage`, `/toggledm`, `/admin`, `/panel`, `/clean`, `/link`, `/botstatus`, `/updatechannels`

### **Economy (8):**
`/balance`, `/daily`, `/weekly`, `/leaderboard`, `/give`, `/coinflip`

### **Giveaways (3):**
`/giveaway`, `/reroll`, `/pick`

### **Music (10):**
`/play`, `/pause`, `/resume`, `/skip`, `/stop`, `/queue`, `/nowplaying`, `/volume`, `/join`, `/leave`

### **Utilities (5):**
`/reactionrole`, `/birthday`, `/afk`, `/serverinfo`, `/userinfo`

### **Fun (5):**
`/roll`, `/8ball`, `/poll`, `/remindme`, `/info`

---

## ⚙️ **CONFIGURATION:**

### **Edit config.py:**

```python
# Channel IDs (right-click → Copy Channel ID)
WELCOME_CHANNEL_ID = 123456789  # Your channel ID
LEAVE_CHANNEL_ID = 123456789
GAME_UPDATE_CHANNEL_ID = 123456789
MUSIC_CHANNEL_ID = 123456789  # Optional

# Images
WELCOME_IMAGE_URL = "https://your-image-url.png"
LEAVE_IMAGE_URL = None

# Developer
DEVELOPER = "YOUR NAME"
DEVELOPER_IDS = [123456789]  # Your Discord user ID

# Auto-DM
DM_JOIN_ENABLED = True
DM_JOIN_MESSAGE = "Welcome {member} to {server}!"
```

---

## 🎯 **FEATURES:**

✅ **50+ Slash Commands**
✅ **Economy & Leveling System**
✅ **Auto XP from chatting**
✅ **Daily/Weekly rewards**
✅ **Giveaway system**
✅ **Music player**
✅ **Reaction roles**
✅ **Birthday announcements**
✅ **Auto-moderation**
✅ **Welcome/Goodbye messages**
✅ **Web admin panel**
✅ **Real-time bot status**
✅ **Daily admin reports**

---

## 📊 **DATA STORAGE:**

Bot creates `data/` folder automatically:
- `economy.json` - User balances & XP
- `reaction_roles.json` - Reaction role configs
- `birthdays.json` - Birthday data
- `web_config.json` - Web panel connection
- `bot_stats.json` - Real-time stats

**Backup these files regularly!**

---

## 🐛 **TROUBLESHOOTING:**

### **Bot won't start:**
- Check bot token is correct in .env
- Verify all dependencies installed
- Check Python version (3.8+)

### **Commands not showing:**
- Wait a few minutes after starting
- Bot auto-syncs commands on startup
- Try `/info` command

### **Economy not saving:**
- Check `data/` folder exists
- Verify file permissions
- Don't force-stop bot (let it save)

### **Music not working:**
- Install FFmpeg on your system
- Check bot has voice permissions
- Join voice channel before `/play`

---

## 📱 **HOSTING OPTIONS:**

| Service | Cost | Uptime | Setup |
|---------|------|--------|-------|
| Replit | FREE | Good* | ⭐⭐⭐⭐⭐ |
| PythonAnywhere | FREE | Excellent | ⭐⭐⭐⭐ |
| Oracle Cloud | FREE | Perfect | ⭐⭐ |
| Railway | FREE 500h | Excellent | ⭐⭐⭐⭐ |
| DigitalOcean | $5/mo | Perfect | ⭐⭐⭐ |

*With UptimeRobot

---

## 🔐 **SECURITY:**

- ✅ Never share .env file
- ✅ Never share bot token
- ✅ Add .env to .gitignore
- ✅ Change web panel password
- ✅ Keep DEVELOPER_IDS updated

---

## 📚 **DOCUMENTATION:**

Read these files for more info:
- `README_ULTRA.md` - Full feature list
- `INSTALLATION_GUIDE.md` - Detailed setup
- `WEB_BRIDGE_GUIDE.md` - Web panel connection
- `CHANGELOG.md` - What's new

---

## 🆘 **NEED HELP?**

1. Check documentation files
2. Use Claude AI in web panel
3. Check Discord.py docs
4. Contact developer

---

## ⚡ **QUICK COMMAND REFERENCE:**

```
# Setup
/link - Link to web panel
/welcome #channel - Set welcome channel
/gamechannel #channel - Set game channel

# Daily Use
/balance - Check stats
/daily - Get free coins
/play song name - Play music
/poll "question?" "opt1" "opt2" - Create poll

# Admin
/panel - Open settings panel
/send #channel message - Send message
/announce text - Post announcement
/giveaway prize:"Gift" duration:60 winners:1
/clean 10 - Delete 10 messages
```

---

## 🎨 **CUSTOMIZATION:**

Everything is customizable:
- Change XP rates in `cogs/economy.py`
- Edit welcome messages in `config.py`
- Customize commands in cog files
- Modify web panel in HTML files
- Adjust timers in `discord_bot.py`

---

## 📄 **LICENSE:**

This bot is for personal/educational use.
Modify and customize as needed!

---

## 🎉 **YOU'RE READY!**

1. Choose hosting method
2. Upload files
3. Add bot token
4. Run bot
5. Enjoy 50+ commands!

**Your complete Discord bot is ready to go! 🚀**

---

**Developer:** SAHAD SHA
**Version:** 2.0 Ultra Edition
**Commands:** 50+
**Last Updated:** April 2026
