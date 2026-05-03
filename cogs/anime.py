# =============================================================================
#  cogs/anime.py — Anime System (Jikan/MyAnimeList API — no key needed)
# =============================================================================

import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import random
import json
import os
from datetime import datetime, time, timezone

JIKAN = "https://api.jikan.moe/v4"

# ── Channel for daily anime post (set in data/settings.json → anime_channel_id)
DEFAULT_ANIME_CHANNEL = None

# Daily post time (UTC)
DAILY_HOUR   = 9
DAILY_MINUTE = 0

GENRE_EMOJIS = {
    "Action": "⚔️", "Adventure": "🗺️", "Comedy": "😂", "Drama": "🎭",
    "Fantasy": "🧙", "Horror": "👻", "Mystery": "🔍", "Romance": "💕",
    "Sci-Fi": "🚀", "Slice of Life": "🌸", "Sports": "🏆", "Supernatural": "✨",
    "Thriller": "😱", "Mecha": "🤖", "Music": "🎵", "Psychological": "🧠",
    "Ecchi": "🔞", "Harem": "💫", "Isekai": "🌀", "Shounen": "💪",
}


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
    image    = (anime.get("images") or {}).get("jpg", {}).get("large_image_url") or \
               (anime.get("images") or {}).get("jpg", {}).get("image_url") or ""

    stars = ""
    try:
        s = float(score)
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
        embed.set_author(name=label, icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")

    embed.add_field(name="⭐ Score",    value=stars,                                  inline=False)
    embed.add_field(name="📺 Episodes", value=str(episodes),                          inline=True)
    embed.add_field(name="📡 Status",   value=f"{_status_emoji(status)} {status}",    inline=True)
    embed.add_field(name="🏅 MAL Rank", value=f"#{rank}",                             inline=True)
    embed.add_field(name="📅 Aired",    value=aired,                                  inline=True)
    embed.add_field(name="👥 Members",  value=f"{members:,}",                         inline=True)
    if genres:
        embed.add_field(name="🎭 Genres", value=_genre_str(genres),                   inline=False)
    if image:
        embed.set_thumbnail(url=image)
    embed.set_footer(text="Data from MyAnimeList via Jikan API")
    return embed


async def _jikan_get(path: str, params: dict = None) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{JIKAN}{path}", params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                return await r.json()
            return {}


# ── Anime search pagination view ────────────────────────────────────────────

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
        anime = self.results[self.index]
        return _build_embed(anime, label=f'Search: "{self.query}"')

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


# ── Top anime list view ─────────────────────────────────────────────────────

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


# ── Main Cog ────────────────────────────────────────────────────────────────

class Anime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot   = bot
        self.daily_posted_date = None
        self.daily_task.start()
        pass  # startup logged by discord_bot.py

    def cog_unload(self):
        self.daily_task.cancel()

    def _anime_channel(self):
        settings = _load_settings()
        cid = settings.get("anime_channel_id") or DEFAULT_ANIME_CHANNEL
        if cid:
            return self.bot.get_channel(int(cid))
        return None

    # ── /anime search ──────────────────────────────────────────────────────

    @discord.app_commands.command(name="anime", description="Search, explore, and discover anime!")
    @discord.app_commands.describe(
        action="What to do",
        query="Anime title (for search only)"
    )
    @discord.app_commands.choices(action=[
        discord.app_commands.Choice(name="🔍 Search",         value="search"),
        discord.app_commands.Choice(name="🏆 Top Anime",      value="top"),
        discord.app_commands.Choice(name="📅 This Season",    value="season"),
        discord.app_commands.Choice(name="🎲 Random",         value="random"),
        discord.app_commands.Choice(name="🔥 Most Popular",   value="popular"),
    ])
    async def anime_cmd(
        self,
        interaction: discord.Interaction,
        action: str,
        query: str = None
    ):
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

    # ── Search ─────────────────────────────────────────────────────────────

    async def _search(self, interaction: discord.Interaction, query: str):
        if not query:
            await interaction.followup.send("❌ Please provide a title to search for.\nExample: `/anime search query:Naruto`", ephemeral=True)
            return

        data = await _jikan_get("/anime", {"q": query, "limit": 10, "sfw": True})
        results = data.get("data", [])

        if not results:
            await interaction.followup.send(f"❌ No results found for **{query}**.", ephemeral=True)
            return

        view  = AnimePageView(results, query)
        embed = view.current_embed()
        await interaction.followup.send(embed=embed, view=view)

    # ── Top ────────────────────────────────────────────────────────────────

    async def _top(self, interaction: discord.Interaction):
        data = await _jikan_get("/top/anime", {"limit": 25})
        items = data.get("data", [])[:25]

        if not items:
            await interaction.followup.send("❌ Could not fetch top anime right now.", ephemeral=True)
            return

        # Split into pages of 5
        pages = []
        for i in range(0, len(items), 5):
            chunk = items[i:i+5]
            desc  = ""
            for idx, a in enumerate(chunk, start=i+1):
                title  = a.get("title_english") or a.get("title") or "Unknown"
                score  = a.get("score") or "N/A"
                eps    = a.get("episodes") or "?"
                url    = a.get("url") or ""
                desc  += f"**#{idx}** [{title}]({url})\n⭐ `{score}/10`  📺 `{eps} eps`\n\n"
            embed = discord.Embed(
                title="🏆 Top Anime — MyAnimeList",
                description=desc,
                color=0xf9c74f
            )
            embed.set_footer(text=f"Top {i+1}–{i+len(chunk)} of 25 · Data from MyAnimeList via Jikan")
            pages.append(embed)

        view = TopAnimeView(pages)
        await interaction.followup.send(embed=pages[0], view=view)

    # ── Season ─────────────────────────────────────────────────────────────

    async def _season(self, interaction: discord.Interaction):
        data = await _jikan_get("/seasons/now", {"limit": 10})
        items = data.get("data", [])[:10]

        if not items:
            await interaction.followup.send("❌ Could not fetch seasonal anime right now.", ephemeral=True)
            return

        now  = datetime.now(timezone.utc)
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

    # ── Random ─────────────────────────────────────────────────────────────

    async def _random(self, interaction: discord.Interaction):
        data = await _jikan_get("/random/anime")
        anime = data.get("data")
        if not anime:
            await interaction.followup.send("❌ Could not fetch a random anime. Try again!", ephemeral=True)
            return
        embed = _build_embed(anime, label="🎲 Random Anime Pick")
        await interaction.followup.send(embed=embed)

    # ── Popular ────────────────────────────────────────────────────────────

    async def _popular(self, interaction: discord.Interaction):
        data = await _jikan_get("/top/anime", {"filter": "bypopularity", "limit": 25})
        items = data.get("data", [])[:25]

        if not items:
            await interaction.followup.send("❌ Could not fetch popular anime right now.", ephemeral=True)
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

    # ── Daily Anime of the Day task ────────────────────────────────────────

    @tasks.loop(minutes=5)
    async def daily_task(self):
        await self.bot.wait_until_ready()
        now = datetime.now(timezone.utc)

        if now.hour != DAILY_HOUR or now.minute // 5 != DAILY_MINUTE // 5:
            return
        if self.daily_posted_date == now.date():
            return

        channel = self._anime_channel()
        if not channel:
            return

        try:
            # Pick from top 100 to keep quality high
            page = random.randint(1, 4)
            data = await _jikan_get("/top/anime", {"limit": 25, "page": page})
            items = data.get("data", [])
            if not items:
                return
            anime = random.choice(items)

            embed = _build_embed(anime, label="🌅 Anime of the Day")
            embed.color = 0xff9f43
            embed.set_author(
                name="✨ Anime of the Day",
                icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
            )

            await channel.send(
                content="🎌 **Good morning anime fans! Here's today's pick!** 🌸",
                embed=embed
            )
            self.daily_posted_date = now.date()
            print(f"🎌 [Anime] Posted Anime of the Day: {anime.get('title')}", flush=True)
        except Exception as e:
            print(f"🎌 [Anime] Daily post error: {e}", flush=True)

    @daily_task.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Anime(bot))
