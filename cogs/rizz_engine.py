# =============================================================================
#  cogs/rizz_engine.py — MINNAL ULTIMATE STREAMING ENGINE
#  Theme: 100+ Anime & Special Grade Developer Lines
# =============================================================================

import discord
from discord.ext import commands, tasks
import random

class RizzEngine(commands.Cog):
    """⚡ The Strongest Engine - 100+ Status Lines"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # 100+ Anime, Tech, and Power-themed lines
        self.rizz_lines = [
            # --- Jujutsu Kaisen / Gojo & Sukuna ---
            "⚡ MINNAL | Special Grade", "🌀 Domain Expansion: Infinite Code",
            "👑 Through Heaven & Earth, I Alone...", "🌪️ Six Eyes: Maximum Output",
            "🩸 Sitting on Sukuna's Throne", "💠 Hollow Purple Execution",
            "💀 Cursed Technique: Reversal", "🤞 Malevolent Shrine: Stable",
            "🎯 Black Flash Logic", "🤞 Unlimited Void: Activated",
            "🌑 The King of Curses", "🧠 0.2s Domain Expansion",
            
            # --- Solo Leveling / Monarch ---
            "⚔️ Arise... Shadow Soldiers", "🏆 Leveling Up Alone...",
            "🛠️ System: Monarch Status", "🌑 The Shadow Monarch",
            "🗡️ Dagger Rush: Critical", "🐉 Beru's Loyalty",
            "🔥 To the Next Gate", "🩸 Bloodlust: Active",
            
            # --- Naruto / Uchiha & Shinobi ---
            "🔥 Amaterasu Strikes", "🌑 Infinite Tsukuyomi Active",
            "👁️ Mangekyou Sharingan: ON", "⚡ Speed of God: Godspeed",
            "🦊 Nine-Tails Chakra", "🌀 Rasengan Logic",
            "🐍 Orochimaru's Lab", "🍂 Will of Fire",
            "👁️ Rinnegan: Almighty Push", "🌩️ Chidori Current",
            
            # --- One Piece / Haki & Pirate ---
            "🏴‍☠️ Conqueror's Haki", "👒 Gear 5: Freedom",
            "🌊 The Great Era of Tech", "⚔️ Santoryu: Secret Skill",
            "🍖 King of the Pirates", "🔥 Red Hawk Execution",
            
            # --- Demon Slayer / Breathing Styles ---
            "⚡ Thunder Breathing: First Form", "🔥 Sun Breathing: Dragon Sun",
            "🌊 Water Surface Slash", "🦋 Butterfly Dance",
            "🌑 Moon Breathing: 14th Form", "🐗 Beast Breathing",
            
            # --- Bleach / Bankai ---
            "⚔️ Bankai: Tensa Zangetsu", "🌑 Getsuga Tenshou",
            "🦋 Espada Level: 0", "🔥 Ryujin Jakka",
            "🌀 Senbonzakura Kageyoshi", "💀 Hollow Mask: Active",
            
            # --- Tech / Developer / Sahad ---
            "💻 Dev: Sahad Sha (The Architect)", "🔊 Voice of the Storm: Sahad",
            "🛠️ System: Optimal", "⚡ /help | Unlock Power",
            "🎯 Debugging Reality", "💾 Zero Latency Life",
            "🚀 Deploying Greatness", "🧠 Neural Link: Secure",
            "🌐 Global Uplink: Active", "📡 Signal: Maximum",
            "⚡ Overclocked Mindset", "⚙️ Hardware: Elite",
            
            # --- Power / Aesthetic / GenZ ---
            "🔥 Lightning Strike", "Welcome to the Void ⚡",
            "💎 Diamond Hands Code", "⚡ Stay High Voltage",
            "👑 The Honored One", "🌪️ Storm Chaser",
            "🌌 Cosmic Energy", "🪐 Gravity Manipulation",
            "⚡ 1,000,000 Volts", "🎭 Ghost in the Shell",
            "🧬 Genetic Evolution", "🦾 Cybernetic Soul",
            "☣️ Biohazard Logic", "🌈 Neon Genesis",
            "🛰️ Satellite Lock: ON", "🔋 100% Charged",
            "⚡ Shockwave Initialized", "🧊 Absolute Zero",
            "🔥 Supernova Status", "🌠 Falling Star",
            "🛡️ Aegis Shield: ON", "⚔️ Blade of the Ruined",
            "🔱 Poseidon's Wrath", "⚡ Zeus's Lightning",
            "🏰 Castle in the Sky", "🏜️ Dune Wanderer",
            "🌋 Magma Heart", "🌀 Hurricane Mind",
            "⚖️ Divine Justice", "🛑 Stop: Reality Check",
            "✨ Pure Aura", "💎 Crystal Clear",
            "⚡ Bolt from the Blue", "🔥 Inferno Protocol",
            "🚀 Beyond the Horizon", "🤖 Android Dreams",
            "📡 Frequency: Alpha", "🌑 Dark Matter",
            "🌟 Stardust Crusader", "⚡ Speed of Light",
            "🧊 Sub-Zero Logic", "🔥 Heat Signature: High",
            "🌊 Tidal Wave Energy", "🌪️ Vortex Active"
        ]
        
        self.stream_url = "https://twitch.tv/discord" 
        self.rotate_status.start()
    
    def cog_unload(self):
        self.rotate_status.cancel()
    
    @tasks.loop(seconds=20) # Fast rotation to show off the variety
    async def rotate_status(self):
        try:
            current_line = random.choice(self.rizz_lines)
            activity = discord.Streaming(name=current_line, url=self.stream_url)
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
        except Exception as e:
            print(f"❌ Status error: {e}", flush=True)

    @rotate_status.before_loop
    async def before_rotate(self):
        await self.bot.wait_until_ready()
        pass  # startup logged by discord_bot.py

    @discord.app_commands.command(name="rizz_check", description="⚡ Scan your current power level")
    async def rizz_check(self, interaction: discord.Interaction):
        score = random.randint(0, 150) # 150 because we are 100+
        
        if score > 120:
            comment = "🏆 **BEYOND SPECIAL GRADE** (Godhood)"
            color = 0xFFD700
        elif score > 90:
            comment = "👑 **Special Grade** (The Honored One)"
            color = 0x9b59b6
        elif score > 70:
            comment = "⚡ **High Grade** (Shadow Monarch)"
            color = 0x3498db
        else:
            comment = "💀 **L Rizz** (Cursed Spirit)"
            color = 0xff4757

        embed = discord.Embed(
            title="` 📡 ` **MINNAL SCANNER**",
            description=f"**{interaction.user.display_name}**, output: `{score}%`",
            color=color
        )
        embed.set_footer(text=f"Verdict: {comment}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(RizzEngine(bot))
