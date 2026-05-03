# =============================================================================
#  cogs/anime.py — Anime System (Jikan/MyAnimeList API — no key needed)
#  Daily Channel Posts:
#    1. Anime Commands Guide  (auto-delete 24h)
#    2. Genre Categories Card (auto-delete 24h)
#    3. Anime of the Day      (auto-delete 24h) — full poster embed
# =============================================================================

import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import random
import json
import os
from datetime import datetime, timezone

JIKAN = "https://api.jikan.moe/v4"

DAILY_HOUR   = 9
DAILY_MINUTE = 0

GENRE_EMOJIS = {
    "Action": "⚔️", "Adventure": "🗺️", "Comedy": "😂", "Drama": "🎭",
    "Fantasy": "🧙", "Horror": "👻", "Mystery": "🔍", "Romance": "💕",
    "Sci-Fi": "🚀", "Slice of Life": "🌸", "Sports": "🏆", "Supernatural": "✨",
    "Thriller": "😱", "Mecha": "🤖", "Music": "🎵", "Psychological": "🧠",
    "Ecchi": "🔞", "Harem": "💫", "Isekai": "🌀", "Shounen": "💪",
}

# Ordered categories for the daily card
CATEGORY_ROWS = [
    [("Action", "⚔️"), ("Adventure", "🗺️"), ("Comedy", "😂"), ("Drama", "🎭")],
    [("Fantasy", "🧙"), ("Horror", "👻"), ("Mystery", "🔍"), ("Romance", "💕")],
    [("Sci-Fi", "🚀"), ("Slice of Life", "🌸"), ("Supernatural", "✨"), ("Mecha", "🤖")],
    [("Psychological", "🧠"), ("Isekai", "🌀"), ("Shounen", "💪"), ("Sports", "🏆")],
]

AOTD_COLOR     = 0xff9f43
COMMANDS_COLOR = 0x7c5cfc
CATEGORY_COLOR = 0x43b89c


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_settings() -> dict:
    try:
        if os.path.exists("data/settings.json"):
            with open("data/settings.json", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _genre_str(genres: list) -> str:
    parts = []
    for g in genres[:5]:
        name = g.get("name", "")
        parts.append(f"{GENRE_EMOJIS.get(name, '🎌')} {name}")
    return "  ".join(parts) if parts else "—"


def _status_emoji(status: str) -> str:
    return {"Currently Airing": "🟢", "Finished Airing": "🔵", "Not yet aired": "🟡"}.get(status, "⚪")


async def _jikan_get(path: str, params: dict = None) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{JIKAN}{path}", params=params,
            timeout=aiohttp.ClientTimeout(total=12)
        ) as r:
            if r.status == 200:
                return await r.json()
            return {}


# ── Embed builders ───────────────────────────────────────────────────────────

def _build_embed(anime: dict, label: str = "") -> discord.Embed:
    title    = anime.get("title_english") or anime.get("title") or "Unknown"
    title_jp = anime.get("title_japanese", "")
    url      = anime.get("url", "")
    synopsis = anime.get("synopsis") or "No synopsis available."
    if len(synopsis) > 400:
        synopsis = synopsis[:400].rsplit(" ", 1)[0] + "…"

    score    = anime.get("score") or "N/A"
    episodes = anime.get("episodes") or "?"
    status   = anime.get("status") or "Unknown"
    aired    = (anime.get("aired") or {}).get("string") or "Unknown"
    rank     = anime.get("rank") or "N/A"
    members  = anime.get("members") or 0
    genres   = anime.get("genres") or []
    images   = (anime.get("images") or {}).get("jpg", {})
    image    = images.get("large_image_url") or images.get("image_url") or ""

    stars = ""
    try:
        s     = float(score)
        full  = int(s // 2)
        half  = 1 if (s % 2) >= 1 else 0
        empty = 5 - full - half
        stars = "⭐" * full + ("✨" if half else "") + "▪️" * empty + f"  **{score}/10**"
    except Exception:
        stars = f"⭐ {score}/10"

    embed = discord.Embed(
        title=f"🎌 {title}",
        description=f"*{title_jp}*\n\n{synopsis}",
        url=url,
        color=0x7c5cfc
    )
    if label:
        embed.set_author(
            name=label,
            icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
        )
    embed.add_field(name="⭐ Score",    value=stars,                               inline=False)
    embed.add_field(name="📺 Episodes", value=str(episodes),                       inline=True)
    embed.add_field(name="📡 Status",   value=f"{_status_emoji(status)} {status}", inline=True)
    embed.add_field(name="🏅 MAL Rank", value=f"#{rank}",                          inline=True)
    embed.add_field(name="📅 Aired",    value=aired,                               inline=True)
    embed.add_field(name="👥 Members",  value=f"{members:,}",                      inline=True)
    if genres:
        embed.add_field(name="🎭 Genres", value=_genre_str(genres),                inline=False)
    if image:
        embed.set_thumbnail(url=image)
    embed.set_footer(text="Data from MyAnimeList via Jikan API")
    return embed


def _build_aotd_embed(anime: dict) -> discord.Embed:
    """Full-poster Anime of the Day embed."""
    title    = anime.get("title_english") or anime.get("title") or "Unknown"
    title_jp = anime.get("title_japanese", "")
    url      = anime.get("url", "")
    synopsis = anime.get("synopsis") or "No synopsis available."
    if len(synopsis) > 380:
        synopsis = synopsis[:380].rsplit(" ", 1)[0] + "…"

    score    = anime.get("score") or "N/A"
    episodes = anime.get("episodes") or "?"
    status   = anime.get("status") or "Unknown"
    rank     = anime.get("rank") or "N/A"
    members  = anime.get("members") or 0
    genres   = anime.get("genres") or []
    images   = (anime.get("images") or {}).get("jpg", {})
    poster   = images.get("large_image_url") or images.get("image_url") or ""

    stars = ""
    try:
        s     = float(score)
        full  = int(s // 2)
        half  = 1 if (s % 2) >= 1 else 0
        empty = 5 - full - half
        stars = "⭐" * full + ("✨" if half else "") + "▪️" * empty + f"  **{score}/10**"
    except Exception:
        stars = f"⭐ {score}/10"

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    embed = discord.Embed(
        title=f"🎌 {title}",
        description=f"*{title_jp}*\n\n{synopsis}",
        url=url,
        color=AOTD_COLOR
    )
    embed.set_author(
        name=f"✨ Anime of the Day  ·  {today}",
        icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
    )
    # Full-width poster as the main image
    if poster:
        embed.set_image(url=poster)

    embed.add_field(name="⭐ Score",      value=stars,                               inline=False)
    embed.add_field(name="📺 Episodes",   value=str(episodes),                       inline=True)
    embed.add_field(name="📡 Status",     value=f"{_status_emoji(status)} {status}", inline=True)
    embed.add_field(name="🏅 MAL Rank",   value=f"#{rank}",                          inline=True)
    embed.add_field(name="👥 Members",    value=f"{members:,}",                      inline=True)
    if genres:
        embed.add_field(name="🎭 Genres", value=_genre_str(genres),                  inline=False)
    embed.set_footer(text="Data from MyAnimeList via Jikan API")
    return embed


def _build_commands_embed() -> discord.Embed:
    """Daily slash commands guide — auto-deletes after 24h."""
    embed = discord.Embed(
        title="⚡ Anime Slash Commands",
        description=(
            "All anime commands available in this server.\n"
            "Type `/` and start typing to use any of them!\n"
        ),
        color=COMMANDS_COLOR
    )
    embed.set_author(
        name="MINNAL  ·  Anime Commands Guide",
        icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
    )

    embed.add_field(
        name="🔍 `/anime search`",
        value="Search any anime by title — paginate through up to 10 results",
        inline=False
    )
    embed.add_field(
        name="🏆 `/anime top`",
        value="Browse the Top 25 highest-rated anime on MyAnimeList",
        inline=False
    )
    embed.add_field(
        name="📅 `/anime season`",
        value="See what's currently airing this season",
        inline=False
    )
    embed.add_field(
        name="🎲 `/anime random`",
        value="Discover a completely random anime — surprise yourself!",
        inline=False
    )
    embed.add_field(
        name="🔥 `/anime popular`",
        value="Most popular anime ranked by total MAL members",
        inline=False
    )
    embed.add_field(
        name="😂 `/animememe`",
        value="Get a random anime meme from Reddit",
        inline=False
    )
    embed.set_footer(text="⏳ This post auto-deletes in 24 hours  ·  New guide posted daily at 9:00 UTC")
    return embed


def _build_categories_embed() -> discord.Embed:
    """Daily genre categories card — auto-deletes after 24h."""
    embed = discord.Embed(
        title="📚 Anime Genre Categories",
        description=(
            "Use `/anime search` with any genre name to explore titles!\n"
            "Or use `/anime random` to discover something new.\n\u200b"
        ),
        color=CATEGORY_COLOR
    )
    embed.set_author(
        name="MINNAL  ·  Genre Explorer",
        icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
    )

    for row in CATEGORY_ROWS:
        row_text = "   ".join(f"{emoji} **{name}**" for name, emoji in row)
        embed.add_field(name="\u200b", value=row_text, inline=False)

    embed.add_field(
        name="\u200b",
        value=(
            "**🌟 Can't decide?**  Try `/anime random` for a surprise pick!\n"
            "**📊 What's trending?**  Use `/anime season` for this season's hits."
        ),
        inline=False
    )
    embed.set_footer(text="Genres sourced from MyAnimeList  ·  Use /anime search <genre> to explore")
    return embed


# ── Pagination Views ─────────────────────────────────────────────────────────

class AnimePageView(discord.ui.View):
    def __init__(self, results: list, query: str):
        super().__init__(timeout=120)
        self.results = results
        self.query   = query
        self.index   = 0
        self._update_buttons()

    def _update_buttons(self):
        self.prev_btn.disabled = (self.index == 0)
        self.next_btn.disabled = (self.index >= len(self.results) - 1)
        self.counter.label     = f"{self.index + 1} / {len(self.results)}"

    def current_embed(self) -> discord.Embed:
        return _build_embed(self.results[self.index], label=f'Search: "{self.query}"')

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    @discord.ui.button(label="1 / 1", style=discord.ButtonStyle.primary, disabled=True)
    async def counter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)


class TopAnimeView(discord.ui.View):
    def __init__(self, pages: list[discord.Embed]):
        super().__init__(timeout=120)
        self.pages = pages
        self.index = 0
        self._update_buttons()

    def _update_buttons(self):
        self.prev_btn.disabled = (self.index == 0)
        self.next_btn.disabled = (self.index >= len(self.pages) - 1)
        self.counter.label     = f"Page {self.index + 1} / {len(self.pages)}"

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @discord.ui.button(label="Page 1 / 1", style=discord.ButtonStyle.primary, disabled=True)
    async def counter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)


# ── Main Cog ──────────────────────────────────────────────────────────────────

class Anime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot               = bot
        self.daily_posted_date = None
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    def _anime_channel(self):
        settings = _load_settings()
        cid = (settings.get("anime") or {}).get("anime_channel_id") or \
              settings.get("anime_channel_id")
        if cid:
            return self.bot.get_channel(int(cid))
        return None

    # ── /anime ────────────────────────────────────────────────────────────

    @discord.app_commands.command(name="anime", description="Search, explore, and discover anime!")
    @discord.app_commands.describe(
        action="What to do",
        query="Anime title (for search only)"
    )
    @discord.app_commands.choices(action=[
        discord.app_commands.Choice(name="🔍 Search",       value="search"),
        discord.app_commands.Choice(name="🏆 Top Anime",    value="top"),
        discord.app_commands.Choice(name="📅 This Season",  value="season"),
        discord.app_commands.Choice(name="🎲 Random",       value="random"),
        discord.app_commands.Choice(name="🔥 Most Popular", value="popular"),
    ])
    async def anime_cmd(self, interaction: discord.Interaction, action: str, query: str = None):
        await interaction.response.defer()
        if action == "search":
            await self._search(interaction, query)
        elif action == "top":
            await self._top(interaction)
        elif action == "season":
            await self._season(interaction)
        elif action == "random":
            await self._random(interaction)
        elif action == "popular":
            await self._popular(interaction)

    # ── Search ────────────────────────────────────────────────────────────

    async def _search(self, interaction: discord.Interaction, query: str):
        if not query:
            await interaction.followup.send(
                "❌ Provide a title.\nExample: `/anime search query:Naruto`", ephemeral=True
            )
            return
        data    = await _jikan_get("/anime", {"q": query, "limit": 10, "sfw": True})
        results = data.get("data", [])
        if not results:
            await interaction.followup.send(f"❌ No results found for **{query}**.", ephemeral=True)
            return
        view  = AnimePageView(results, query)
        await interaction.followup.send(embed=view.current_embed(), view=view)

    # ── Top ───────────────────────────────────────────────────────────────

    async def _top(self, interaction: discord.Interaction):
        data  = await _jikan_get("/top/anime", {"limit": 25})
        items = data.get("data", [])[:25]
        if not items:
            await interaction.followup.send("❌ Could not fetch top anime.", ephemeral=True)
            return
        pages = []
        for i in range(0, len(items), 5):
            chunk = items[i:i+5]
            desc  = ""
            for idx, a in enumerate(chunk, start=i+1):
                title = a.get("title_english") or a.get("title") or "Unknown"
                score = a.get("score") or "N/A"
                eps   = a.get("episodes") or "?"
                url   = a.get("url") or ""
                desc += f"**#{idx}** [{title}]({url})\n⭐ `{score}/10`  📺 `{eps} eps`\n\n"
            embed = discord.Embed(title="🏆 Top Anime — MyAnimeList", description=desc, color=0xf9c74f)
            embed.set_footer(text=f"Top {i+1}–{i+len(chunk)} of 25 · Data from MyAnimeList via Jikan")
            pages.append(embed)
        view = TopAnimeView(pages)
        await interaction.followup.send(embed=pages[0], view=view)

    # ── Season ────────────────────────────────────────────────────────────

    async def _season(self, interaction: discord.Interaction):
        data  = await _jikan_get("/seasons/now", {"limit": 10})
        items = data.get("data", [])[:10]
        if not items:
            await interaction.followup.send("❌ Could not fetch seasonal anime.", ephemeral=True)
            return
        now         = datetime.now(timezone.utc)
        season_name = ["Winter", "Spring", "Summer", "Fall"][(now.month - 1) // 3]
        desc = ""
        for a in items:
            title  = a.get("title_english") or a.get("title") or "Unknown"
            score  = a.get("score") or "?"
            eps    = a.get("episodes") or "?"
            url    = a.get("url") or ""
            genres = "  ".join(g["name"] for g in (a.get("genres") or [])[:3])
            desc  += f"**[{title}]({url})**\n⭐ `{score}`  📺 `{eps} eps`  🎭 {genres or '—'}\n\n"
        embed = discord.Embed(
            title=f"📅 {season_name} {now.year} — Currently Airing",
            description=desc,
            color=0x43b89c
        )
        embed.set_footer(text="Data from MyAnimeList via Jikan API")
        await interaction.followup.send(embed=embed)

    # ── Random ────────────────────────────────────────────────────────────

    async def _random(self, interaction: discord.Interaction):
        data  = await _jikan_get("/random/anime")
        anime = data.get("data")
        if not anime:
            await interaction.followup.send("❌ Could not fetch a random anime. Try again!", ephemeral=True)
            return
        await interaction.followup.send(embed=_build_embed(anime, label="🎲 Random Anime Pick"))

    # ── Popular ───────────────────────────────────────────────────────────

    async def _popular(self, interaction: discord.Interaction):
        data  = await _jikan_get("/top/anime", {"filter": "bypopularity", "limit": 25})
        items = data.get("data", [])[:25]
        if not items:
            await interaction.followup.send("❌ Could not fetch popular anime.", ephemeral=True)
            return
        pages = []
        for i in range(0, len(items), 5):
            chunk = items[i:i+5]
            desc  = ""
            for idx, a in enumerate(chunk, start=i+1):
                title   = a.get("title_english") or a.get("title") or "Unknown"
                members = a.get("members") or 0
                score   = a.get("score") or "N/A"
                url     = a.get("url") or ""
                desc   += f"**#{idx}** [{title}]({url})\n👥 `{members:,} members`  ⭐ `{score}/10`\n\n"
            embed = discord.Embed(
                title="🔥 Most Popular Anime — MyAnimeList",
                description=desc,
                color=0xff6b6b
            )
            embed.set_footer(text=f"Top {i+1}–{i+len(chunk)} of 25 · Data from MyAnimeList via Jikan")
            pages.append(embed)
        view = TopAnimeView(pages)
        await interaction.followup.send(embed=pages[0], view=view)

    # ── Daily Task — 3 cards posted every day at 9:00 UTC ─────────────────

    @tasks.loop(minutes=5)
    async def daily_task(self):
        await self.bot.wait_until_ready()
        now = datetime.now(timezone.utc)

        # Fire at 09:00 UTC only (5-min window)
        if now.hour != DAILY_HOUR or now.minute // 5 != DAILY_MINUTE // 5:
            return
        if self.daily_posted_date == now.date():
            return

        channel = self._anime_channel()
        if not channel:
            import logger as log
            log.warning("anime", "No anime channel configured — skipping daily post")
            return

        try:
            DELETE = 86400  # 24 hours in seconds

            # ── Card 1: Slash Commands Guide (auto-deletes in 24h) ────────
            await channel.send(
                content="📌 **Today's Anime Commands** — use these slash commands!",
                embed=_build_commands_embed(),
                delete_after=DELETE
            )
            await asyncio.sleep(1.5)

            # ── Card 2: Genre Categories (permanent) ──────────────────────
            await channel.send(
                content="🗂️ **Browse by Genre** — explore the anime world!",
                embed=_build_categories_embed()
            )
            await asyncio.sleep(1.5)

            # ── Card 3: Anime of the Day (permanent, full poster) ─────────
            page  = random.randint(1, 4)
            data  = await _jikan_get("/top/anime", {"limit": 25, "page": page})
            items = data.get("data", [])
            if items:
                anime = random.choice(items)
                await channel.send(
                    content="🌅 **Anime of the Day!** Good morning, anime fans! 🌸",
                    embed=_build_aotd_embed(anime)
                )
                import logger as log
                log.event("anime", f"Daily posts sent → #{channel.name}  |  AotD: {anime.get('title')}")

            self.daily_posted_date = now.date()

        except Exception as e:
            import logger as log
            log.error("anime", f"Daily post failed: {e}")

    @daily_task.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Anime(bot))
