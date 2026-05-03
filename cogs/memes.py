# =============================================================================
#  cogs/memes.py — Anime Memes & Troll System
# =============================================================================

import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import random
import asyncio
import os
from datetime import datetime


TROLL_MESSAGES = [
    "Looks like {target} got hit by Sukuna's Domain Expansion! 💀",
    "{target} when they think they have a chance against me 🤡",
    "Bro {target} thinks they're the main character 😂",
    "{target} after losing the plot armor: 💀",
    "{target} when Gojo says 'I alone am the honored one' 😎",
    "{target} POV: You vs Goku at full power 🤣",
    "{target} trying to act tough be like: 🥲",
    "{target} energy when they're about to lose: 💀",
    "Imagine being {target} 💀 (couldn't be me)",
    "{target} watching me cast Domain Expansion: 😱",
    "{target} when they realize they're a side character 😭",
    "Naruto would beat {target} 🤣",
    "{target} thinks they have plot armor like Luffy 💀",
    "If {target} was in anime, they'd be filler 😂",
    "{target} can't even handle Genin techniques 🤡",
    "Goku could one shot {target} 🥱",
    "{target} when Itachi uses Tsukuyomi: 🥶",
    "{target}'s power level: less than Yamcha 💀",
    "{target} is the type to challenge Saitama 😂",
    "Even Krillin would beat {target} 🤣",
    "{target} thinks they have rizz like Gojo 💀💀💀",
    "Real ninjas don't talk like {target} 🤡",
    "{target} couldn't survive in AOT for 5 minutes 😭"
]

TROLL_EMOJIS = ["💀", "🤣", "😭", "🤡", "😎", "😏", "🥱", "🥲", "🤪", "😈"]

ANIME_FACTS = [
    "🎌 One Piece has been running since 1997!",
    "🎌 Goku has died more times than any other anime hero!",
    "🎌 Demon Slayer broke box office records globally!",
    "🎌 Attack on Titan's manga ended in April 2021!",
    "🎌 Sukuna has 4 arms and 2 faces in his original form!",
    "🎌 The word 'anime' comes from 'animation'!",
    "🎌 Pikachu's name combines 'pika' and 'chu'!",
    "🎌 Luffy's bounty has reached 3 billion berries!",
    "🎌 Eren's last name 'Yeager' means 'hunter' in German!",
    "🎌 Naruto's headband symbol means 'shinobi'!",
    "🎌 Death Note's L sits weirdly to increase brain function!",
    "🎌 Studio Ghibli films have won an Oscar!",
    "🎌 Sailor Moon was banned in some countries!",
    "🎌 Gojo's character is voiced by Yuichi Nakamura!"
]

ANIME_QUOTES = [
    "📖 \"Throughout heaven and earth, I alone am the honored one.\" - Gojo",
    "📖 \"I'm gonna be the King of the Pirates!\" - Luffy",
    "📖 \"Believe it!\" - Naruto",
    "📖 \"Plus Ultra!\" - All Might",
    "📖 \"Bankai!\" - Ichigo",
    "📖 \"This is the strongest!\" - Gojo",
    "📖 \"A lesson without pain is meaningless.\" - Edward Elric",
    "📖 \"If you don't take risks, you can't create a future!\" - Luffy",
    "📖 \"I'll take a potato chip... AND EAT IT!\" - Light",
    "📖 \"People die when they are killed.\" - Shirou",
    "📖 \"Power comes in response to a need.\" - Goku",
    "📖 \"The world isn't perfect, but it's there for us.\" - Roy Mustang",
    "📖 \"Talent doesn't matter. Hard work always wins.\" - Rock Lee",
    "📖 \"The moment you give up is the moment you let someone else win.\" - Kobe Bryant"
]


class MemeSystem(commands.Cog):
    """Anime Memes & Troll Commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.meme_channel_id = int(os.getenv('MEME_CHANNEL_ID', '0'))
        self.daily_meme_task.start()
        pass  # startup logged by discord_bot.py
    
    def cog_unload(self):
        self.daily_meme_task.cancel()
        if self.session:
            asyncio.create_task(self.session.close())
    
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def fetch_anime_meme(self):
        try:
            session = await self.get_session()
            subreddits = ["Animemes", "AnimeFunny", "wholesomeanimemes", "goodanimemes"]
            subreddit = random.choice(subreddits)
            url = f"https://www.reddit.com/r/{subreddit}/random/.json"
            headers = {'User-Agent': 'MINNAL Bot 1.0'}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        post = data[0]['data']['children'][0]['data']
                    else:
                        return None
                    
                    if not post.get('url', '').endswith(('.jpg', '.png', '.gif', '.jpeg')):
                        preview = post.get('preview', {})
                        images = preview.get('images', [])
                        if images:
                            url = images[0].get('source', {}).get('url', '').replace('&amp;', '&')
                            if url:
                                post['url'] = url
                            else:
                                return None
                        else:
                            return None
                    
                    return {
                        'title': post.get('title', 'Anime Meme'),
                        'url': post['url'],
                        'subreddit': subreddit,
                        'upvotes': post.get('ups', 0)
                    }
        except Exception as e:
            print(f"❌ Meme fetch error: {e}", flush=True)
            return None
    
    @tasks.loop(hours=24)
    async def daily_meme_task(self):
        try:
            if self.meme_channel_id == 0:
                return
            
            channel = self.bot.get_channel(self.meme_channel_id)
            if not channel:
                return
            
            meme = await self.fetch_anime_meme()
            if not meme:
                return
            
            embed = discord.Embed(
                title=f"🎌 Daily Anime Meme",
                description=f"**{meme['title']}**",
                color=discord.Color.purple(),
                timestamp=datetime.utcnow()
            )
            embed.set_image(url=meme['url'])
            embed.add_field(name="📍 From", value=f"r/{meme['subreddit']}", inline=True)
            embed.add_field(name="⬆️ Upvotes", value=str(meme['upvotes']), inline=True)
            embed.set_footer(text="MINNAL Bot ⚡")
            
            await channel.send(embed=embed)
            print(f"✅ Daily meme posted", flush=True)
        except Exception as e:
            print(f"❌ Daily meme error: {e}", flush=True)
    
    @daily_meme_task.before_loop
    async def before_daily_meme(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(10)
    
    @app_commands.command(name="meme", description="🎭 Get random anime meme")
    @app_commands.describe(target="Optional: Mention to troll someone")
    async def meme_command(self, interaction: discord.Interaction, target: discord.Member = None):
        await interaction.response.defer()
        
        meme = await self.fetch_anime_meme()
        if not meme:
            await interaction.followup.send("❌ Could not fetch meme!")
            return
        
        if target:
            troll_message = random.choice(TROLL_MESSAGES).format(target=target.mention)
            emoji = random.choice(TROLL_EMOJIS)
            
            embed = discord.Embed(
                title=f"{emoji} GET TROLLED! {emoji}",
                description=troll_message,
                color=discord.Color.red()
            )
            embed.set_image(url=meme['url'])
            embed.add_field(name="🎯 Target", value=target.mention, inline=True)
            embed.add_field(name="🎪 By", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"r/{meme['subreddit']} • MINNAL Bot")
            
            await interaction.followup.send(content=target.mention, embed=embed)
        else:
            embed = discord.Embed(
                title=f"🎌 {meme['title']}",
                color=discord.Color.purple()
            )
            embed.set_image(url=meme['url'])
            embed.add_field(name="📍 From", value=f"r/{meme['subreddit']}", inline=True)
            embed.add_field(name="⬆️ Upvotes", value=str(meme['upvotes']), inline=True)
            embed.set_footer(text="🎭 Use /meme @user to troll!")
            
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="troll", description="😈 Troll someone with anime meme")
    @app_commands.describe(target="Person to troll")
    async def troll_command(self, interaction: discord.Interaction, target: discord.Member):
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ Can't troll yourself! 🤡", ephemeral=True)
            return
        
        if target.bot:
            await interaction.response.send_message("❌ Can't troll bots!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        meme = await self.fetch_anime_meme()
        if not meme:
            await interaction.followup.send("❌ Memes not loading!")
            return
        
        troll_message = random.choice(TROLL_MESSAGES).format(target=target.mention)
        emoji = random.choice(TROLL_EMOJIS)
        
        embed = discord.Embed(
            title=f"{emoji} TROLL ATTACK! {emoji}",
            description=troll_message,
            color=discord.Color.red()
        )
        embed.set_image(url=meme['url'])
        embed.add_field(name="🎯 Victim", value=target.mention, inline=True)
        embed.add_field(name="🎪 By", value=interaction.user.mention, inline=True)
        embed.set_footer(text="MINNAL Bot 💀")
        
        await interaction.followup.send(content=f"{target.mention} TROLLED! 💀", embed=embed)
    
    @app_commands.command(name="animememe", description="🎌 Random anime meme, quote or fact")
    async def anime_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        choice = random.choice(['meme', 'quote', 'fact', 'meme', 'meme'])
        
        if choice == 'meme':
            meme = await self.fetch_anime_meme()
            if not meme:
                await interaction.followup.send("❌ No content!")
                return
            embed = discord.Embed(title=f"🎌 {meme['title']}", color=discord.Color.purple())
            embed.set_image(url=meme['url'])
            embed.set_footer(text=f"r/{meme['subreddit']}")
            await interaction.followup.send(embed=embed)
        elif choice == 'quote':
            quote = random.choice(ANIME_QUOTES)
            embed = discord.Embed(title="💬 Anime Quote", description=quote, color=discord.Color.gold())
            await interaction.followup.send(embed=embed)
        else:
            fact = random.choice(ANIME_FACTS)
            embed = discord.Embed(title="🎌 Anime Fact", description=fact, color=discord.Color.blue())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="quote", description="💬 Random anime quote")
    async def quote_command(self, interaction: discord.Interaction):
        quote = random.choice(ANIME_QUOTES)
        embed = discord.Embed(title="💬 Anime Quote", description=quote, color=discord.Color.gold())
        embed.set_footer(text="MINNAL Bot")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="animefact", description="🎌 Random anime fact")
    async def fact_command(self, interaction: discord.Interaction):
        fact = random.choice(ANIME_FACTS)
        embed = discord.Embed(title="🎌 Anime Fact", description=fact, color=discord.Color.blue())
        embed.set_footer(text="MINNAL Bot")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="memenow", description="🚀 Force post meme NOW (Admin)")
    async def memenow_command(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Admin only!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        if self.meme_channel_id == 0:
            await interaction.followup.send("❌ Set MEME_CHANNEL_ID first!")
            return
        
        channel = self.bot.get_channel(self.meme_channel_id)
        if not channel:
            await interaction.followup.send("❌ Channel not found!")
            return
        
        meme = await self.fetch_anime_meme()
        if not meme:
            await interaction.followup.send("❌ Could not fetch meme!")
            return
        
        embed = discord.Embed(
            title=f"🎌 Anime Meme",
            description=f"**{meme['title']}**",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.set_image(url=meme['url'])
        embed.add_field(name="📍 From", value=f"r/{meme['subreddit']}", inline=True)
        embed.add_field(name="⬆️ Upvotes", value=str(meme['upvotes']), inline=True)
        embed.set_footer(text="MINNAL Bot ⚡")
        
        await channel.send(embed=embed)
        await interaction.followup.send(f"✅ Posted in {channel.mention}!")
    
    @app_commands.command(name="setmemechannel", description="📌 Set meme channel (Admin)")
    @app_commands.describe(channel="Channel for daily memes")
    async def set_meme_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ Admin only!", ephemeral=True)
            return
        
        self.meme_channel_id = channel.id
        
        embed = discord.Embed(
            title="📌 Meme Channel Set",
            description=f"Daily memes → {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="💡 Tip", value=f"Add `MEME_CHANNEL_ID = {channel.id}` to Railway!", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MemeSystem(bot))