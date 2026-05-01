# ⚡ MINNAL BOT - ULTRA EDITION
## The Most Powerful Discord Bot for Friends Servers

---

## 🌟 **COMPLETE FEATURE LIST**

### 🔐 **Admin Commands**
- `/send` - Send messages to any channel
- `/embed` - Send rich embeds
- `/announce` - Post styled announcements
- `/gameupdate` - Post game updates
- `/post` - Send colored styled posts
- `/welcome` - Set welcome channel
- `/leavechannel` - Set goodbye channel
- `/gamechannel` - Set game updates channel
- `/setwelcomeimage` - Set/clear welcome image
- `/setleaveimage` - Set/clear goodbye image
- `/setmusicchannel` - Lock music to a channel
- `/clearmusicchannel` - Remove music restrictions
- `/setdmmessage` - Edit auto-DM template
- `/toggledm` - Enable/disable auto-DM
- `/admin` - View admin dashboard
- `/panel` - Open interactive settings panel
- `/clean` - Delete messages (1-100)

---

### 🎵 **Music System**
- `/play` - Play songs from YouTube
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/skip` - Skip current song
- `/stop` - Stop and clear queue
- `/queue` - View music queue
- `/nowplaying` - Show current song
- `/volume` - Adjust volume (1-100)
- `/join` - Join voice channel
- `/leave` - Leave voice channel

---

### 💰 **Economy & Leveling** ⭐ NEW
- **Auto XP System** - Earn XP by chatting (5-15 XP per message)
- **Level Up Rewards** - Get coins when you level up
- `/balance` - Check balance, level, XP, and progress
- `/daily` - Claim daily reward (500+ coins)
- `/weekly` - Claim weekly reward (5000+ coins)
- `/leaderboard` - View top users (balance/level/messages)
- `/give` - Transfer coins to other users
- `/coinflip` - Bet coins on heads/tails

**Features:**
- 📊 XP Progress Bar
- 💵 Virtual Currency
- 🏆 Level-based Bonuses
- 📈 Message Tracking
- 🎰 Gambling Games

---

### 🎉 **Giveaways & Events** ⭐ NEW
- `/giveaway` - Start a giveaway (Admin)
  - Set prize, duration, number of winners
  - Auto-pick winners when time ends
- `/reroll` - Reroll giveaway winner (Admin)
- `/pick` - Pick random server members (1-10)

**Features:**
- 🎁 Automatic Winner Selection
- ⏰ Countdown Timer
- 🎊 Multiple Winners Support
- 🔄 Reroll Functionality

---

### 🎮 **Fun Commands**
- `/roll` - Roll dice (1d6, 2d20, etc.)
- `/8ball` - Ask magic 8-ball
- `/poll` - Create reaction polls (up to 5 options)
- `/remindme` - Set reminders (10m, 2h, 1d)
- `/coinflip` - Gambling game

---

### 🛠️ **Utility Commands** ⭐ NEW
- `/reactionrole` - Create self-assign roles (Admin)
- `/birthday` - Set your birthday
- `/afk` - Set AFK status
- `/serverinfo` - View server stats
- `/userinfo` - View user information

**Features:**
- 📋 Reaction Roles (click emoji = get role)
- 🎂 Birthday Announcements (automatic)
- 💤 AFK System
- ℹ️ Detailed Server/User Info

---

### 🤖 **Auto Features**
- ✅ Welcome messages with custom images
- ✅ Goodbye messages
- ✅ Auto-DM new members
- ✅ Daily game updates (9 AM)
- ✅ XP gain from chatting
- ✅ Level up notifications
- ✅ Birthday announcements
- ✅ Dynamic music status

---

## 📊 **FEATURE COMPARISON**

| Feature | Basic Bots | MINNAL Ultra |
|---------|------------|--------------|
| Music Player | ✅ | ✅ |
| Welcome/Goodbye | ✅ | ✅ |
| Economy System | ❌ | ✅ |
| Leveling System | ❌ | ✅ |
| Giveaways | ❌ | ✅ |
| Reaction Roles | ❌ | ✅ |
| Birthday System | ❌ | ✅ |
| Gambling | ❌ | ✅ |
| Leaderboards | ❌ | ✅ |
| Auto XP | ❌ | ✅ |
| **Total Commands** | ~20 | **50+** |

---

## 🚀 **QUICK START GUIDE**

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Bot Token
Create `.env` file:
```
DISCORD_BOT_TOKEN=your_token_here
```

### 3. Configure Settings
Edit `config.py` or use the web admin panel:
```
https://minnal-admin-panel.netlify.app/
Password: MINNAL@2025
```

### 4. Run the Bot
```bash
python discord_bot.py
```

---

## 📋 **SETUP CHECKLIST**

### Initial Setup
- [ ] Set bot token in `.env`
- [ ] Configure channel IDs in `config.py`
- [ ] Upload welcome/goodbye images
- [ ] Set developer name
- [ ] Enable required Discord intents

### In-Server Setup
- [ ] Run `/panel` to configure via Discord
- [ ] Set welcome channel with `/welcome`
- [ ] Set game channel with `/gamechannel`
- [ ] Set music channel (optional) with `/setmusicchannel`
- [ ] Create reaction roles with `/reactionrole`
- [ ] Test all features!

---

## 🎯 **RECOMMENDED SETUP FOR FRIENDS SERVER**

### 1. **Economy Settings**
- Enable daily/weekly rewards
- Let friends earn XP by chatting
- Host giveaways with prizes

### 2. **Reaction Roles**
Create roles for:
- 🎮 Gamers
- 🎵 Music Lovers
- 🎬 Movie Night
- 📢 Announcements
- 🎉 Events

### 3. **Birthday System**
- Everyone sets their birthday with `/birthday`
- Bot announces on their special day

### 4. **Music Setup**
- Create dedicated music text channel
- Create dedicated music voice channel
- Lock music commands to that channel

### 5. **Giveaways**
- Regular giveaways for game keys
- Event participation rewards
- Monthly prizes for top users

---

## 📁 **FILE STRUCTURE**

```
MINNAL-BOT/
├── discord_bot.py          # Main bot file
├── config.py               # Configuration
├── .env                    # Bot token (DO NOT SHARE)
├── requirements.txt        # Dependencies
├── cogs/
│   ├── admin.py           # Admin commands
│   ├── music.py           # Music system
│   ├── fun.py             # Fun commands
│   ├── info.py            # Info panel
│   ├── economy.py         # Economy & Leveling ⭐ NEW
│   ├── giveaways.py       # Giveaways & Events ⭐ NEW
│   ├── utilities.py       # Utilities & Tools ⭐ NEW
│   └── checks.py          # Permission checks
└── data/                   # Auto-created data storage
    ├── economy.json        # User balances & XP
    ├── reaction_roles.json # Reaction role configs
    └── birthdays.json      # Birthday data
```

---

## 🔧 **WEB ADMIN PANEL**

Access your bot settings from any browser:

```
URL: https://minnal-admin-panel.netlify.app/
Password: MINNAL@2025
```

### Features:
- 📱 Mobile-friendly
- ⚙️ Configure all settings
- 💬 Generate Discord commands
- 📦 Export config.py
- 🔐 Password protected

### Tabs:
1. **Configuration** - Channel IDs, images, developer info
2. **Messages** - Generate send/embed/announce commands
3. **Channels** - Set welcome/leave/game/music channels
4. **Quick Commands** - Generate fun commands
5. **Export Config** - Download config.py

---

## 💡 **PRO TIPS**

### For Server Owners:
1. **Use `/panel`** in Discord for quick settings changes
2. **Create reaction roles** for self-service role assignment
3. **Host weekly giveaways** to keep members engaged
4. **Check `/leaderboard`** to see most active members
5. **Use `/serverinfo`** to track server growth

### For Members:
1. **Chat regularly** to earn XP and level up
2. **Claim `/daily`** every 24 hours for free coins
3. **Set your `/birthday`** to get celebrated
4. **Use `/balance`** to track your progress
5. **Join giveaways** by reacting with 🎉

---

## 🆘 **TROUBLESHOOTING**

### Bot Not Responding?
- Check bot is online in Discord
- Verify permissions (Admin, Send Messages, Embed Links)
- Make sure Message Content Intent is enabled

### Commands Not Syncing?
- Bot auto-syncs on startup
- Wait a few minutes after starting
- Try `/info` to test

### Economy Not Saving?
- Make sure `data/` folder exists
- Check file permissions
- Don't force-stop the bot (let it save first)

### Music Not Working?
- Check FFmpeg is installed
- Verify bot has voice permissions
- Make sure you're in a voice channel

---

## 📈 **FUTURE UPDATES**

Coming soon:
- 🎰 More gambling games (slots, blackjack)
- 🏪 Item shop (buy items with coins)
- 🎯 Achievement system
- 📊 Advanced statistics dashboard
- 🎨 Custom embed builder
- 🔔 Custom notification system
- 🎭 Role-play commands
- 📝 Suggestion system with voting

---

## 🎉 **COMMAND QUICK REFERENCE**

### Most Used Commands:
```
/balance        - Check your stats
/daily          - Free daily coins
/play           - Play music
/poll           - Create a poll
/giveaway       - Start giveaway (Admin)
/serverinfo     - Server information
/leaderboard    - Top users
```

### Admin Commands:
```
/panel          - Settings panel
/send           - Send message
/announce       - Make announcement
/reactionrole   - Create reaction role
/giveaway       - Start giveaway
/clean          - Delete messages
```

---

## 📄 **LICENSE**

This bot is for personal/educational use.

---

## 👨‍💻 **DEVELOPER**

**SAHAD SHA**

For support or questions, contact the bot developer.

---

**🎮 MINNAL BOT - Making Discord Servers More Fun!**

Version: 2.0 Ultra Edition
Last Updated: April 2026
