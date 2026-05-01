# =============================================================================
#  cogs/fun.py — Fun & utility commands
#  Commands: /roll  /8ball  /remindme  /clean  /poll
# =============================================================================

import asyncio
import random
import re
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from cogs.checks import is_admin


class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /roll ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="roll", description="Roll a dice — e.g. 1d6, 2d20, d100")
    @app_commands.describe(dice="Dice notation like 1d6 or 2d20 (default: 1d6)")
    async def slash_roll(self, interaction: discord.Interaction, dice: str = "1d6"):
        match = re.fullmatch(r'(\d+)?d(\d+)', dice.strip().lower())
        if not match:
            return await interaction.response.send_message(
                "❌ Use dice notation like `1d6`, `2d20`, or `d100`.", ephemeral=True
            )
        count = int(match.group(1) or 1)
        sides = int(match.group(2))
        if count < 1 or count > 20 or sides < 2:
            return await interaction.response.send_message(
                "❌ Use between 1–20 dice with at least 2 sides.", ephemeral=True
            )
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        roll_str = " + ".join(str(r) for r in rolls) if count > 1 else str(rolls[0])
        embed = discord.Embed(
            title=f"🎲 Rolling {dice.lower()}",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="Result",
            value=f"**{roll_str}**" + (f" = **{total}**" if count > 1 else ""),
            inline=False
        )
        embed.set_footer(text=f"Rolled by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /8ball ────────────────────────────────────────────────────────────────
    @app_commands.command(name="8ball", description="Ask the magic 8-ball a yes/no question")
    @app_commands.describe(question="Your yes/no question")
    async def slash_8ball(self, interaction: discord.Interaction, question: str):
        responses = [
            ("🟢", "It is certain."),      ("🟢", "It is decidedly so."),
            ("🟢", "Without a doubt."),    ("🟢", "Yes, definitely."),
            ("🟢", "You may rely on it."), ("🟢", "As I see it, yes."),
            ("🟢", "Most likely."),        ("🟢", "Outlook good."),
            ("🟢", "Yes."),               ("🟢", "Signs point to yes."),
            ("🟡", "Reply hazy, try again."),   ("🟡", "Ask again later."),
            ("🟡", "Better not tell you now."), ("🟡", "Cannot predict now."),
            ("🟡", "Concentrate and ask again."),
            ("🔴", "Don't count on it."), ("🔴", "My reply is no."),
            ("🔴", "My sources say no."), ("🔴", "Outlook not so good."),
            ("🔴", "Very doubtful."),
        ]
        dot, answer = random.choice(responses)
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.dark_purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="❓ Question",    value=question,        inline=False)
        embed.add_field(name=f"{dot} Answer", value=f"**{answer}**", inline=False)
        embed.set_footer(text=f"Asked by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /remindme ─────────────────────────────────────────────────────────────
    @app_commands.command(name="remindme", description="Set a reminder — bot will DM you after the time")
    @app_commands.describe(time="Time until reminder, e.g. 10m, 2h, 1d", reminder="What to remind you about")
    async def slash_remindme(self, interaction: discord.Interaction, time: str, reminder: str):
        match = re.fullmatch(r'(\d+)([mhd])', time.strip().lower())
        if not match:
            return await interaction.response.send_message("❌ Use `10m`, `2h`, or `1d` format.", ephemeral=True)
        amount, unit = int(match.group(1)), match.group(2)
        seconds = amount * {'m': 60, 'h': 3600, 'd': 86400}[unit]
        if seconds > 7 * 86400:
            return await interaction.response.send_message("❌ Maximum reminder time is 7 days.", ephemeral=True)
        label = f"{amount} {'minute' if unit=='m' else 'hour' if unit=='h' else 'day'}{'s' if amount != 1 else ''}"
        await interaction.response.send_message(
            f"✅ Got it! I'll remind you about **{reminder}** in **{label}**.", ephemeral=True
        )

        async def send_reminder():
            await asyncio.sleep(seconds)
            try:
                embed = discord.Embed(
                    title="⏰ Reminder!",
                    description=reminder,
                    color=discord.Color.yellow(),
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text="You asked me to remind you")
                await interaction.user.send(embed=embed)
            except discord.Forbidden:
                pass

        self.bot.loop.create_task(send_reminder())

    # ── /clean ────────────────────────────────────────────────────────────────
    @app_commands.command(name="clean", description="Delete recent messages in this channel (Admin only)")
    @app_commands.describe(amount="Number of messages to delete (1–100)")
    @is_admin()
    async def slash_clean(self, interaction: discord.Interaction, amount: int):
        if not 1 <= amount <= 100:
            return await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(
            f"🧹 Deleted **{len(deleted)}** message{'s' if len(deleted) != 1 else ''}.", ephemeral=True
        )

    # ── /poll ─────────────────────────────────────────────────────────────────
    @app_commands.command(name="poll", description="Create a poll with up to 5 options")
    @app_commands.describe(
        question="The poll question",
        option1="Option 1", option2="Option 2",
        option3="Option 3 (optional)", option4="Option 4 (optional)", option5="Option 5 (optional)"
    )
    async def slash_poll(
        self,
        interaction: discord.Interaction,
        question: str, option1: str, option2: str,
        option3: str = None, option4: str = None, option5: str = None
    ):
        options   = [o for o in [option1, option2, option3, option4, option5] if o]
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        embed = discord.Embed(
            title="📊 " + question,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.description = '\n'.join(f"{reactions[i]} {opt}" for i, opt in enumerate(options))
        embed.set_footer(text=f"Poll by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        for i in range(len(options)):
            await message.add_reaction(reactions[i])


async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
