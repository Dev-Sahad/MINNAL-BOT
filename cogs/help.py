# =============================================================================
#  cogs/help.py — Catalogue-Style /help Command
#  Dropdown category selector, paginated command listings, live bot stats
# =============================================================================

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

# ── Command Catalogue ──────────────────────────────────────────────────────
# Format: { category_label: { emoji, description, commands: [(name, desc)] } }

CATALOGUE = {
    "🎌 Anime": {
        "emoji": "🎌",
        "color": 0x7c5cfc,
        "description": "Explore anime, get daily picks, and search MyAnimeList.",
        "commands": [
            ("/anime search",   "Search any anime by title — cover, score, synopsis, genres"),
            ("/anime top",      "Top 25 highest rated anime on MyAnimeList"),
            ("/anime popular",  "Top 25 most followed anime by member count"),
            ("/anime season",   "All anime currently airing this season"),
            ("/anime random",   "Random anime pick from the top database"),
            ("/animememe",      "Random anime meme, quote or fun fact"),
            ("/quote",          "Random anime quote from iconic characters"),
            ("/animefact",      "Interesting anime trivia and facts"),
        ]
    },
    "🎵 Music": {
        "emoji": "🎵",
        "color": 0x1db954,
        "description": "Full music system — play, queue, control, and stream.",
        "commands": [
            ("/play",        "Play a song or playlist by name/URL"),
            ("/pause",       "Pause the current track"),
            ("/resume",      "Resume playback"),
            ("/skip",        "Skip to the next song in queue"),
            ("/stop",        "Stop music and clear the queue"),
            ("/queue",       "View the current music queue"),
            ("/nowplaying",  "Show what's currently playing"),
            ("/join",        "Pull the bot into your voice channel"),
            ("/leave",       "Disconnect the bot from voice"),
        ]
    },
    "🏆 Levels & XP": {
        "emoji": "🏆",
        "color": 0xf9c74f,
        "description": "Earn XP by chatting and climb the server ranks.",
        "commands": [
            ("/rank",        "View your XP rank card — level, progress bar, server position"),
            ("/rank @user",  "Check anyone else's rank card"),
            ("/xptop",       "Top 10 members by XP with medals 🥇🥈🥉"),
            ("/addxp",       "⚙️ [Admin] Add XP to a member"),
            ("/setlevel",    "⚙️ [Admin] Set a member's level directly"),
            ("/resetxp",     "⚙️ [Admin] Wipe a member's XP to zero"),
        ]
    },
    "💰 Economy": {
        "emoji": "💰",
        "color": 0xf4d03f,
        "description": "Earn, spend and gamble your server coins.",
        "commands": [
            ("/balance",      "Check your coin balance"),
            ("/daily",        "Claim your daily coin reward"),
            ("/weekly",       "Claim your weekly coin bonus"),
            ("/give",         "Give coins to another member"),
            ("/leaderboard",  "Top coin holders in the server"),
        ]
    },
    "🎮 Fun & Games": {
        "emoji": "🎮",
        "color": 0xff6b6b,
        "description": "Games, randomness and entertainment for everyone.",
        "commands": [
            ("/8ball",       "Ask the magic 8-ball any yes/no question"),
            ("/roll",        "Roll dice — e.g. `/roll 2d6`"),
            ("/coinflip",    "Flip a coin — heads or tails"),
            ("/pick",        "Bot picks randomly from your options"),
            ("/poll",        "Create a reaction poll with up to 5 options"),
            ("/rizz_check",  "Rate your rizz level 🔥"),
            ("/ask",         "Ask the bot anything for a fun answer"),
            ("/troll",       "Troll a server member with a meme"),
        ]
    },
    "🎁 Giveaways": {
        "emoji": "🎁",
        "color": 0xff9f43,
        "description": "Create and manage server giveaways.",
        "commands": [
            ("/giveaway",  "Start a giveaway in any channel"),
            ("/reroll",    "Pick a new winner for a finished giveaway"),
        ]
    },
    "🛡️ Moderation": {
        "emoji": "🛡️",
        "color": 0xe74c3c,
        "description": "Keep your server clean and under control.",
        "commands": [
            ("/clear",           "⚙️ Delete a number of messages from a channel"),
            ("/clean",           "⚙️ Bulk-delete messages with filters"),
            ("/say",             "⚙️ Make the bot say something"),
            ("/meme",            "Post a random meme"),
            ("/memenow",         "Force-post a meme immediately"),
            ("/setmemechannel",  "⚙️ Set the auto-meme channel"),
            ("/reactionrole",    "⚙️ Set up reaction-to-role messages"),
        ]
    },
    "🌀 Voice & Domains": {
        "emoji": "🌀",
        "color": 0x9b59b6,
        "description": "Dynamic voice channels and domain expansion spells.",
        "commands": [
            ("/spell",             "Cast an anime voice spell in a voice channel"),
            ("/listvoices",        "List all available voice spells"),
            ("/listdomains",       "List all active domain channels"),
            ("/domaininfo",        "Info about a specific domain channel"),
            ("/domainrename",      "⚙️ Rename a domain channel"),
            ("/domainlock",        "⚙️ Lock a domain channel"),
            ("/domainunlock",      "⚙️ Unlock a domain channel"),
            ("/domainkick",        "⚙️ Kick all members from a domain"),
            ("/setdomaintrigger",  "⚙️ Set the channel that creates domains"),
        ]
    },
    "🔧 Utility": {
        "emoji": "🔧",
        "color": 0x43b89c,
        "description": "Handy tools for everyday server life.",
        "commands": [
            ("/remindme",    "Set a reminder — bot DMs you after the time"),
            ("/birthday",    "Set your birthday for server announcements"),
            ("/serverinfo",  "Show detailed server information"),
            ("/userinfo",    "Show info about any server member"),
            ("/codepilot",   "AI-powered code help and review"),
            ("/link",        "Share a useful link in a formatted embed"),
            ("/info",        "Bot info, live stats and latency"),
        ]
    },
    "⚙️ Bot & Admin": {
        "emoji": "⚙️",
        "color": 0x7a7a9a,
        "description": "Admin panel, Railway logs and bot configuration.",
        "commands": [
            ("/panel",       "Open the web admin panel link"),
            ("/webpanel",    "Web panel status and link"),
            ("/webstats",    "Live bot and server statistics"),
            ("/relay_now",   "⚙️ Manually trigger Railway log relay to Discord"),
        ]
    },
}


# ── Category overview embed ────────────────────────────────────────────────

def build_overview(bot: commands.Bot) -> discord.Embed:
    embed = discord.Embed(
        title="📖 MINNAL Command Catalogue",
        description=(
            "Pick a **category** from the dropdown below to browse commands.\n"
            f"**{sum(len(v['commands']) for v in CATALOGUE.values())} commands** across "
            f"**{len(CATALOGUE)} categories**.\n\u200b"
        ),
        color=0x7c5cfc,
        timestamp=datetime.now(timezone.utc)
    )

    for label, data in CATALOGUE.items():
        count = len(data["commands"])
        embed.add_field(
            name=f"{data['emoji']} {label.split(' ', 1)[1]}",
            value=f"`{count} commands`\n{data['description']}",
            inline=True
        )

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(
        text=f"MINNAL · {round(bot.latency * 1000)}ms  |  Use the dropdown ↓",
        icon_url=bot.user.display_avatar.url
    )
    return embed


# ── Category detail embed ──────────────────────────────────────────────────

def build_category(label: str, bot: commands.Bot) -> discord.Embed:
    data  = CATALOGUE[label]
    lines = []
    for name, desc in data["commands"]:
        admin = desc.startswith("⚙️")
        lines.append(f"**`{name}`**\n{'⚙️ ' if admin else ''}{'  ' if not admin else ''}{desc.replace('⚙️ ', '')}")

    embed = discord.Embed(
        title=f"{label}",
        description=data["description"] + "\n\u200b",
        color=data["color"],
        timestamp=datetime.now(timezone.utc)
    )
    # Split into two columns
    half = (len(lines) + 1) // 2
    left  = "\n\n".join(lines[:half])
    right = "\n\n".join(lines[half:])
    if left:
        embed.add_field(name="\u200b", value=left,  inline=True)
    if right:
        embed.add_field(name="\u200b", value=right, inline=True)

    embed.set_footer(
        text=f"MINNAL · {len(data['commands'])} commands in this category  |  ⚙️ = Admin only",
        icon_url=bot.user.display_avatar.url
    )
    return embed


# ── Dropdown Select ────────────────────────────────────────────────────────

class CategorySelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        options  = [
            discord.SelectOption(
                label=label.split(" ", 1)[1],   # label without emoji
                value=label,
                emoji=data["emoji"],
                description=data["description"][:100]
            )
            for label, data in CATALOGUE.items()
        ]
        super().__init__(
            placeholder="📂 Choose a category…",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        chosen = self.values[0]
        embed  = build_category(chosen, self.bot)
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=180)
        self.bot = bot
        self.add_item(CategorySelect(bot))

    @discord.ui.button(label="🏠 Overview", style=discord.ButtonStyle.secondary, row=1)
    async def home_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = build_overview(self.bot)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


# ── Cog ───────────────────────────────────────────────────────────────────

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        pass  # startup logged by discord_bot.py

    @app_commands.command(name="help", description="Browse all MINNAL commands by category")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = build_overview(self.bot)
        view  = HelpView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
