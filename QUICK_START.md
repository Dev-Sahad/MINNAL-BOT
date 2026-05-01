# ⚡ MINNAL BOT - QUICK START GUIDE
## Get Your Bot Online in 10 Minutes!

---

## 📦 **YOU HAVE:**
- ✅ Complete bot with 50+ commands
- ✅ Web admin panel
- ✅ All documentation
- ✅ Ready to deploy!

---

## 🚀 **3 WAYS TO HOST (NO GITHUB NEEDED!):**

---

### **METHOD 1: REPLIT** ⭐ EASIEST (10 minutes)

**Step 1:** Go to **replit.com** → Sign up with email

**Step 2:** Create New Repl → Choose **Python**

**Step 3:** Upload ALL files from this folder

**Step 4:** In Replit, click **Tools** → **Secrets** → Add:
```
Key: DISCORD_BOT_TOKEN
Value: [paste your bot token here]
```

**Step 5:** Create a file called `main.py`:
```python
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "MINNAL Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
os.system('python discord_bot.py')
```

**Step 6:** Click **RUN** button (big green button)

**Step 7:** ✅ Bot is online!

**Keep it 24/7:**
- Copy your Replit URL
- Go to **uptimerobot.com** → Create free account
- Add monitor → Paste Replit URL → Set interval to 5 minutes
- ✅ Bot stays online forever!

---

### **METHOD 2: PYTHONANYWHERE** (Free 24/7)

**Step 1:** Go to **pythonanywhere.com** → Sign up

**Step 2:** Click **Files** → Upload all files from this folder

**Step 3:** Go to **Consoles** → Start Bash console

**Step 4:** Run these commands:
```bash
cd minnal-bot
pip3 install --user -r requirements.txt
echo "DISCORD_BOT_TOKEN=your_token_here" > .env
```

**Step 5:** Go to **Tasks** → Create Always-On Task:
```
Command: python3 /home/yourusername/minnal-bot/discord_bot.py
```

**Step 6:** ✅ Bot runs 24/7 for free!

---

### **METHOD 3: YOUR COMPUTER** (Testing only)

**Step 1:** Install Python 3.8+ from python.org

**Step 2:** Open terminal/command prompt

**Step 3:** Navigate to this folder:
```bash
cd path/to/MINNAL-BOT-COMPLETE
```

**Step 4:** Install dependencies:
```bash
pip install -r requirements.txt
```

**Step 5:** Create `.env` file with your token:
```
DISCORD_BOT_TOKEN=your_actual_bot_token_here
```

**Step 6:** Run the bot:
```bash
python discord_bot.py
```

**Step 7:** ✅ Bot online (only when computer is on!)

---

## 🎯 **WHAT TO DO FIRST:**

### **After Bot is Online:**

1. **Test it:** Type `/info` in Discord
2. **Set channels:** `/welcome #channel`
3. **Link web panel:** `/link`
4. **Try economy:** `/daily`
5. **Play music:** `/play song name`

### **Configure:**

Edit `config.py`:
```python
WELCOME_CHANNEL_ID = 123456789  # Your channel ID
DEVELOPER = "YOUR NAME"
DEVELOPER_IDS = [123456789]  # Your Discord ID
```

---

## 🌐 **WEB PANEL SETUP:**

**Step 1:** Go to **netlify.com** → Drop & deploy

**Step 2:** Drag `advanced-admin-panel.html` into Netlify

**Step 3:** Your panel is live!

**Step 4:** Default password: `MINNAL@2025`

**Step 5:** In Discord: `/link` → Copy token → Paste in web panel

---

## ✅ **CHECKLIST:**

- [ ] Choose hosting method (Replit recommended)
- [ ] Upload bot files
- [ ] Add bot token
- [ ] Run bot
- [ ] Test with `/info` command
- [ ] Set welcome channel with `/welcome`
- [ ] Deploy web panel to Netlify
- [ ] Link bot to web with `/link`
- [ ] Change web panel password
- [ ] ✅ Done! Enjoy 50+ commands!

---

## 📂 **FILES INCLUDED:**

```
MINNAL-BOT-COMPLETE/
├── discord_bot.py              # Main bot
├── config.py                   # Settings
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── README_ULTRA.md             # Full docs
├── WEB_BRIDGE_GUIDE.md         # Web connection
├── INSTALLATION_GUIDE.md       # Detailed setup
├── advanced-admin-panel.html   # Web panel
├── cogs/                       # 9 feature cogs
│   ├── admin.py               # 17 commands
│   ├── economy.py             # 8 commands
│   ├── giveaways.py           # 3 commands
│   ├── music.py               # 10 commands
│   ├── fun.py                 # 5 commands
│   ├── utilities.py           # 5 commands
│   ├── info.py                # Info panel
│   ├── web_bridge.py          # 4 commands
│   └── checks.py              # Permissions
└── data/                       # Auto-created
```

---

## 💬 **COMMANDS QUICK REFERENCE:**

```
/info - Command list
/balance - Check stats
/daily - Free coins
/play song - Play music
/giveaway - Start giveaway
/poll - Create poll
/welcome #channel - Set welcome
/link - Link web panel
/botstatus - Bot dashboard
```

---

## 🆘 **NEED HELP?**

1. **Read:** `README_ULTRA.md` for full docs
2. **Check:** `INSTALLATION_GUIDE.md` for setup help
3. **Web Guide:** `WEB_BRIDGE_GUIDE.md` for web panel
4. **Ask Claude AI:** In your web panel!

---

## ⚠️ **IMPORTANT:**

- Never share your `.env` file
- Never share bot token
- Change web panel password
- Backup `data/` folder regularly

---

## 🎉 **YOU'RE READY!**

Choose your hosting method above and get started!

**Recommended:** Replit + UptimeRobot = FREE 24/7 bot!

---

**Developer:** SAHAD SHA  
**Version:** 2.0 Ultra  
**Commands:** 50+  
**Support:** Use Claude AI in web panel!

⚡ **MINNAL BOT - Unleash the Power!** ⚡
