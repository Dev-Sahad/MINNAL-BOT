# 🚀 MINNAL BOT ULTRA - INSTALLATION GUIDE

## ⚡ **WHAT'S NEW IN ULTRA EDITION**

### 🎉 **3 NEW FEATURE PACKS ADDED:**

#### 1️⃣ **💰 Economy & Leveling System** (`cogs/economy.py`)
- Auto XP gain from chatting
- Level up rewards
- Virtual currency
- Daily/Weekly rewards
- Leaderboards
- Coin transfers
- Gambling (coinflip)

**New Commands:**
- `/balance` - Check stats
- `/daily` - Daily reward
- `/weekly` - Weekly reward
- `/leaderboard` - Top users
- `/give` - Transfer coins
- `/coinflip` - Gamble

#### 2️⃣ **🎁 Giveaways & Events** (`cogs/giveaways.py`)
- Automated giveaways
- Random winner selection
- Multiple winners support
- Reroll functionality
- Random member picker

**New Commands:**
- `/giveaway` - Start giveaway (Admin)
- `/reroll` - Reroll winner (Admin)
- `/pick` - Pick random members

#### 3️⃣ **🛠️ Utilities Pack** (`cogs/utilities.py`)
- Reaction roles (self-assign)
- Birthday system (auto-announce)
- AFK system
- Server/User info
- Auto-moderation ready

**New Commands:**
- `/reactionrole` - Create reaction roles (Admin)
- `/birthday` - Set birthday
- `/afk` - Set AFK status
- `/serverinfo` - Server info
- `/userinfo` - User info

---

## 📦 **INSTALLATION**

### **Option 1: Fresh Install (New Bot)**

1. **Download all files** from `MINNAL-BOT-ULTRA/`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file:**
```
DISCORD_BOT_TOKEN=your_token_here
```

4. **Run the bot:**
```bash
python discord_bot.py
```

5. **Done!** All features are active!

---

### **Option 2: Upgrade Existing Bot**

If you already have the MINNAL bot running:

1. **Backup your current bot folder**

2. **Copy these NEW files to your bot folder:**
   - `cogs/economy.py`
   - `cogs/giveaways.py`
   - `cogs/utilities.py`

3. **Replace these files:**
   - `discord_bot.py` (updated cog loader)
   - `README_ULTRA.md` (new documentation)

4. **Keep your existing:**
   - `config.py` (your settings)
   - `.env` (your token)
   - `cogs/admin.py` (fixed version)
   - Other cogs

5. **Restart the bot**

6. **Data folders will auto-create:**
   - `data/economy.json`
   - `data/reaction_roles.json`
   - `data/birthdays.json`

---

## ✅ **VERIFICATION**

Test that everything works:

```
/info           - Should show 50+ commands
/balance        - Should show your profile
/daily          - Should give you coins
/serverinfo     - Should show server stats
```

---

## 🎯 **FIRST-TIME SETUP**

### **1. Set Up Economy**
- Members start earning XP immediately
- First person to chat gets XP!
- Check leaderboard: `/leaderboard`

### **2. Create Reaction Roles**
Example:
```
/reactionrole emoji:🎮 role:@Gamer description:For gamers
/reactionrole emoji:🎵 role:@Music description:Music lovers
```

### **3. Set Birthdays**
Tell everyone to use:
```
/birthday month:4 day:15
```

### **4. Host First Giveaway**
```
/giveaway prize:"Discord Nitro" duration:60 winners:1
```
(60 = 60 minutes)

---

## 📊 **DATA STORAGE**

All user data is stored locally in `data/` folder:

- `economy.json` - Balances, XP, levels
- `reaction_roles.json` - Reaction role configs
- `birthdays.json` - Birthday data

**⚠️ IMPORTANT:**
- Backup these files regularly
- Don't delete while bot is running
- Data persists across restarts

---

## 🔧 **CUSTOMIZATION**

### **Economy Settings**

Edit in `cogs/economy.py`:

```python
# XP per message
xp_gain = random.randint(5, 15)  # Change range

# Daily reward
base_reward = 500  # Change amount

# Level up reward
reward = user_data['level'] * 100  # Change formula
```

### **Birthday Channel**

Edit in `cogs/utilities.py`:

```python
# Find channel name
channel = discord.utils.get(guild.text_channels, name="general")
```
Change `"general"` to your channel name

---

## 🎨 **WEB ADMIN PANEL**

The admin panel now supports all new features!

```
URL: https://minnal-admin-panel.netlify.app/
Password: MINNAL@2025
```

You can generate commands for:
- Economy commands
- Giveaway setup
- Reaction role creation
- And more!

---

## 🐛 **TROUBLESHOOTING**

### **Economy not saving?**
- Check `data/` folder exists
- Make sure bot has write permissions
- Let bot gracefully shutdown (Ctrl+C, wait for save)

### **Reaction roles not working?**
- Check bot has "Manage Roles" permission
- Bot's role must be HIGHER than roles it assigns
- Emoji must be exact match

### **Birthdays not announcing?**
- Bot checks once per day at midnight UTC
- Make sure bot is running 24/7
- Check bot has permission in announcement channel

### **Giveaways ending early?**
- Bot must stay online for duration
- Use hosting service for 24/7 uptime
- Active giveaways lost if bot restarts

---

## 📈 **HOSTING RECOMMENDATIONS**

For 24/7 uptime:

**Free Options:**
- Railway.app (500 hrs/month free)
- Render.com (750 hrs/month free)
- Heroku (discontinued free tier)

**Paid Options:**
- DigitalOcean ($5/month)
- AWS EC2 (various pricing)
- Linode ($5/month)

**Required for:**
- Birthday announcements (needs 24/7)
- Giveaway timers (needs to stay online)
- Daily reward resets

---

## 📚 **FULL COMMAND LIST**

### **Economy (8 commands)**
- `/balance` `/daily` `/weekly` `/leaderboard`
- `/give` `/coinflip`

### **Giveaways (3 commands)**
- `/giveaway` `/reroll` `/pick`

### **Utilities (5 commands)**
- `/reactionrole` `/birthday` `/afk`
- `/serverinfo` `/userinfo`

### **Music (10 commands)**
- `/play` `/pause` `/resume` `/skip` `/stop`
- `/queue` `/nowplaying` `/volume` `/join` `/leave`

### **Admin (17 commands)**
- `/send` `/embed` `/announce` `/gameupdate` `/post`
- `/welcome` `/leavechannel` `/gamechannel`
- `/setwelcomeimage` `/setleaveimage`
- `/setmusicchannel` `/clearmusicchannel`
- `/setdmmessage` `/toggledm` `/admin` `/panel` `/clean`

### **Fun (5 commands)**
- `/roll` `/8ball` `/poll` `/remindme` `/info`

**TOTAL: 50+ Commands!**

---

## 🎯 **RECOMMENDED FIRST STEPS**

1. ✅ Install and start the bot
2. ✅ Run `/panel` to configure channels
3. ✅ Create 3-5 reaction roles
4. ✅ Tell everyone to set birthdays
5. ✅ Host a test giveaway
6. ✅ Check `/leaderboard` after a few hours
7. ✅ Share `/daily` command with everyone
8. ✅ Have fun!

---

## 💡 **PRO TIPS**

1. **Pin important commands** in a channel:
   ```
   📌 Useful Commands:
   /balance - Check your stats
   /daily - Free coins every 24h
   /weekly - Free coins every 7 days
   /leaderboard - Top users
   ```

2. **Announce new features:**
   ```
   /announce announcement:🎉 NEW BOT FEATURES!
   - Earn XP by chatting
   - Daily/Weekly rewards
   - Set your birthday with /birthday
   - Check /info for all commands!
   ```

3. **Host regular events:**
   - Weekly giveaways
   - Monthly leaderboard prizes
   - Birthday celebrations

---

## 🔒 **SECURITY NOTES**

- Never share your `.env` file
- Keep `data/` folder private
- Don't give bot admin permission (only needed roles)
- Regular backups of `data/` folder
- Change admin panel password

---

## 🆘 **SUPPORT**

If you need help:
1. Check README_ULTRA.md
2. Read troubleshooting section
3. Test each feature individually
4. Check bot console for errors

---

**🎮 You now have the MOST POWERFUL Discord bot for your friends server!**

Enjoy! ⚡
