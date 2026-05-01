# 🔗 WEBHOOK SYSTEM - COMPLETE SETUP GUIDE

## Real-Time Communication: Discord Bot ↔ Web Panel

---

## 🎯 **WHAT IS THIS?**

A **webhook server** that creates **real-time** communication between your Discord bot and web panel!

### **Without Webhooks:**
```
Web Panel → Reads JSON files → Every 30 seconds
❌ Delays
❌ No real-time updates
❌ No web → bot commands
```

### **With Webhooks:**
```
Bot ↔ Webhook Server ↔ Web Panel
✅ Real-time updates (instant!)
✅ Live stats
✅ Send commands from web to bot
✅ Track events as they happen
```

---

## 📦 **FILES CREATED:**

### **1. `webhook_server.py`** - Webhook Server
The middleman between bot and web panel

**Features:**
- Receives bot stats every 2 minutes
- Sends stats to web panel
- Accepts commands from web
- Logs all activity
- Secure authentication

### **2. `cogs/web_bridge.py`** - Updated Bot Cog
Bot side of webhook system

**New Features:**
- Sends stats to webhook every 2 minutes
- Sends events (member join, commands used)
- Checks for commands from web every 30 seconds
- Executes web commands

### **3. `webhook_panel_integration.html`** - Web Panel Code
Web panel side of webhook system

**Features:**
- Connect to webhook server
- Real-time bot stats
- Command statistics
- Activity logs
- Send messages from web

---

## 🚀 **SETUP INSTRUCTIONS:**

### **Step 1: Host Webhook Server**

You need to host `webhook_server.py` on a server. Options:

#### **Option A: Render.com** (Recommended)

1. Go to **render.com**
2. Click **"New +"** → **"Web Service"**
3. Connect your code or upload ZIP:
   - `webhook_server.py`
   - `requirements.txt` (add `flask` and `flask-cors`)
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python webhook_server.py`
5. Add Environment Variable:
   - Key: `WEBHOOK_SECRET`
   - Value: (generate random string)
6. Deploy!
7. Copy your webhook URL: `https://your-app.onrender.com`

#### **Option B: Railway.app**

1. Create new project
2. Upload webhook server files
3. Add environment variables
4. Deploy
5. Get URL

#### **Option C: Same Server as Bot**

If bot runs on a VPS:
```bash
# Install dependencies
pip install flask flask-cors

# Run webhook server
python webhook_server.py &
```

---

### **Step 2: Update Bot Files**

#### **Update requirements.txt:**
```
discord.py>=2.7.0
python-dotenv>=1.0.0
yt-dlp>=2024.0.0
PyNaCl>=1.5.0
aiohttp>=3.8.0
flask>=2.3.0
flask-cors>=4.0.0
```

#### **Copy Updated Files:**
- Copy new `cogs/web_bridge.py` to your bot
- Restart bot

---

### **Step 3: Link Bot to Webhook**

In Discord, run:
```
/link webhook_url:https://your-webhook-server.com
```

You'll get:
```
✅ Web Panel Linked!
🔑 Server Token: abc123...
🔗 Webhook Secret: xyz789...
📡 Webhook URL: https://your-webhook-server.com
```

**Copy all three values!**

---

### **Step 4: Add Webhook Tab to Web Panel**

Open `advanced-admin-panel.html`:

1. **Add Tab:**
```html
<div class="tab" onclick="switchTab('webhook')">🔗 Webhook</div>
```

2. **Copy content from** `webhook_panel_integration.html`

3. **Save and re-upload to Netlify**

---

### **Step 5: Connect Web Panel**

1. Open your web panel
2. Go to **"Webhook"** tab
3. Enter:
   - **Webhook URL:** `https://your-webhook-server.com`
   - **Server Token:** (from /link command)
   - **Webhook Secret:** (from /link command)
4. Click **"Connect"**
5. ✅ See real-time stats!

---

## 🔄 **HOW IT WORKS:**

### **Data Flow:**

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Discord Bot    │────────►│ Webhook Server   │◄────────│  Web Panel       │
│                 │         │  (Middleman)     │         │  (Netlify)       │
└─────────────────┘         └──────────────────┘         └──────────────────┘
     │                              │                             │
     │ Every 2 min:                 │ Stores:                     │ Every 10 sec:
     │ - Send stats                 │ - Bot stats                 │ - Fetch stats
     │ - Send events                │ - Events                    │ - Get logs
     │ Every 30 sec:                │ - Commands                  │ On demand:
     │ - Check commands             │                             │ - Send commands
     │                              │                             │ - Update settings
```

### **Events Tracked:**

- ✅ Member joins
- ✅ Member leaves
- ✅ Commands used
- ✅ Bot status changes
- ✅ Channel updates
- ✅ Setting changes

---

## 📊 **WEBHOOK ENDPOINTS:**

### **Bot → Webhook:**

```
POST /webhook/bot/stats
- Send bot statistics
- Every 2 minutes
- Requires webhook secret

POST /webhook/bot/event
- Send events (member join, command used)
- Real-time
- Requires webhook secret
```

### **Web → Webhook:**

```
GET /webhook/web/stats
- Get current bot stats
- Requires server token

POST /webhook/web/settings
- Update bot settings
- Requires server token

POST /webhook/web/command
- Send command to bot
- Requires server token

GET /webhook/web/command-stats
- Get command usage stats
- Requires server token

GET /webhook/logs
- Get recent webhook activity
- Requires server token
```

### **Health Check:**

```
GET /webhook/health
- Check if webhook server is online
- No authentication required
```

---

## ✨ **NEW FEATURES:**

### **1. Real-Time Stats**
See bot status update every 10 seconds in web panel!

### **2. Live Activity Feed**
Watch as members join, commands are used, etc.

### **3. Web → Bot Commands**
Send messages from web panel to Discord!

### **4. Command Statistics**
See which commands are most popular

### **5. Activity Logs**
View last 100 webhook events

---

## 🎯 **USE CASES:**

### **Monitor Bot from Anywhere:**
- Open web panel on phone
- See live stats
- No need to open Discord

### **Send Messages Remotely:**
- Type in web panel
- Sends to Discord channel
- Perfect for announcements

### **Track Activity:**
- See when members join
- Watch command usage
- Spot trends

### **Quick Updates:**
- Change channels from web
- Update settings remotely
- No bot restart needed

---

## 🔐 **SECURITY:**

### **Three Layers:**

1. **Webhook Secret** - Bot to Webhook auth
2. **Server Token** - Web to Webhook auth
3. **HTTPS** - All connections encrypted

### **Best Practices:**

- ✅ Never share webhook secret
- ✅ Never share server token
- ✅ Use HTTPS for webhook server
- ✅ Rotate tokens monthly
- ✅ Monitor webhook logs

---

## 📱 **WEB PANEL FEATURES:**

### **Webhook Tab Shows:**

- 🔗 Connection status
- 📊 Real-time bot stats
- ⚡ Command statistics
- 📜 Recent activity logs
- 📤 Quick message sender

### **Auto-Refresh:**

- Stats: Every 10 seconds
- Logs: On demand
- Status: Continuous

---

## 🆘 **TROUBLESHOOTING:**

### **Webhook server offline**
```bash
# Check if server is running
curl https://your-webhook-server.com/webhook/health

# Should return:
{
  "status": "online",
  "service": "MINNAL Webhook Server"
}
```

### **Web panel can't connect**
1. Check webhook URL is correct
2. Verify server token matches
3. Check webhook server is running
4. Try health check endpoint

### **Bot not sending updates**
1. Check `webhook_url` in web_config.json
2. Verify webhook secret is correct
3. Check bot logs for errors
4. Restart bot

### **Commands from web not working**
1. Check bot is checking for commands (every 30 sec)
2. Verify server token is correct
3. Check webhook server logs
4. Try manual test

---

## 💡 **TESTING:**

### **Test Webhook Health:**
```bash
curl https://your-webhook-server.com/webhook/health
```

### **Test Bot → Webhook:**
Wait 2 minutes after bot starts, check webhook server logs

### **Test Web → Webhook:**
In web panel, try sending a message

---

## 📋 **CHECKLIST:**

- [ ] Host webhook server on Render/Railway
- [ ] Copy webhook URL
- [ ] Update bot's `web_bridge.py`
- [ ] Add `flask` and `flask-cors` to requirements.txt
- [ ] Restart bot
- [ ] Run `/link` with webhook URL
- [ ] Copy server token and webhook secret
- [ ] Add webhook tab to web panel
- [ ] Upload panel to Netlify
- [ ] Connect web panel to webhook
- [ ] ✅ See real-time updates!

---

## 🎨 **CUSTOMIZATION:**

### **Change Update Frequency:**

**In `web_bridge.py`:**
```python
@tasks.loop(minutes=2)  # Change to 1, 5, 10, etc.
async def webhook_send_task(self):
```

**In `webhook_panel_integration.html`:**
```javascript
updateInterval = setInterval(() => {
    fetchBotStats();
}, 10000);  // Change to 5000, 20000, etc.
```

### **Add Custom Events:**

**In bot code:**
```python
await self.send_webhook_event('custom_event', {
    'data': 'your data here'
})
```

### **Add Custom Endpoints:**

**In `webhook_server.py`:**
```python
@app.route('/webhook/custom', methods=['POST'])
def custom_endpoint():
    # Your code here
    return jsonify({'success': True})
```

---

## 🚀 **BENEFITS:**

✅ **Real-time** - No delays, instant updates  
✅ **Two-way** - Web can control bot  
✅ **Secure** - Token-based authentication  
✅ **Scalable** - Handle multiple bots  
✅ **Logged** - Track all activity  
✅ **Fast** - Updates every 10 seconds  
✅ **Reliable** - Auto-reconnect  

---

## 📊 **COMPARISON:**

| Feature | Without Webhooks | With Webhooks |
|---------|------------------|---------------|
| Update Speed | 30 seconds | 10 seconds |
| Web → Bot | ❌ No | ✅ Yes |
| Event Tracking | ❌ No | ✅ Yes |
| Activity Logs | ❌ No | ✅ Yes |
| Real-time | ❌ No | ✅ Yes |
| Command Stats | ❌ No | ✅ Yes |

---

## 🎯 **NEXT STEPS:**

1. **Host webhook server** (Render.com recommended)
2. **Update bot files**
3. **Run `/link` with webhook URL**
4. **Update web panel**
5. **Connect and enjoy real-time updates!**

---

**YOUR BOT AND WEB PANEL ARE NOW CONNECTED IN REAL-TIME! 🔗⚡**

Need help? Check the troubleshooting section or ask Claude AI in your web panel!
