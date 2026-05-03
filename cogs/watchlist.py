# =============================================================================
#  cogs/watchlist.py — Personal Anime Watchlist
#  Commands:
#    /watchlist add <query>    — Search & add anime to your list
#    /watchlist view           — Browse your watchlist (paginated)
#    /watchlist remove <num>   — Remove an entry by number
#    /watchlist clear          — Wipe your entire list
# =============================================================================

import discord
from discord.ext import commands
import aiohttp
import json
import os
from datetime import datetime, timezone

JIKAN      = "https://api.jikan.moe/v4"
DATA_FILE  = "data/watchlist.json"
MAX_PER_USER = 50   # cap per member
PAGE_SIZE    = 5    # entries per view-page

GENRE_EMOJIS = {
    "Action": "⚔️", "Adventure": "🗺️", "Comedy": "😂", "Drama": "🎭",
    "Fantasy": "🧙", "Horror": "👻", "Mystery": "🔍", "Romance": "💕",
    "Sci-Fi": "🚀", "Slice of Life": "🌸", "Sports": "🏆", "Supernatural": "✨",
    "Thriller": "😱", "Mecha": "🤖", "Psychological": "🧠", "Isekai": "🌀",
    "Shounen": "💪", "Music": "🎵",
}

ACCENT = 0x7c5cfc


# ── Storage helpers ───────────────────────────────────────────────────────────

def _load() -> dict:
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _user_list(data: dict, uid: str) -> list:
    return data.setdefault(uid, [])


# ── Jikan helper ──────────────────────────────────────────────────────────────

async def _search(query: str) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{JIKAN}/anime",
            params={"q": query, "limit": 5, "sfw": True},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            if r.status == 200:
                return (await r.json()).get("data", [])
    return []


def _entry_from_anime(anime: dict) -> dict:
    genres = [g["name"] for g in (anime.get("genres") or [])[:4]]
    images = (anime.get("images") or {}).get("jpg", {})
    return {
        "mal_id":   anime.get("mal_id"),
        "title":    anime.get("title_english") or anime.get("title") or "Unknown",
        "title_jp": anime.get("title_japanese") or "",
        "url":      anime.get("url") or "",
        "score":    anime.get("score") or "N/A",
        "episodes": anime.get("episodes") or "?",
        "status":   anime.get("status") or "Unknown",
        "image":    images.get("large_image_url") or images.get("image_url") or "",
        "genres":   genres,
        "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


# ── Embed builders ────────────────────────────────────────────────────────────

def _status_dot(status: str) -> str:
    return {"Currently Airing": "🟢", "Finished Airing": "🔵", "Not yet aired": "🟡"}.get(status, "⚪")


def _confirm_embed(anime: dict, query: str) -> discord.Embed:
    title   = anime.get("title_english") or anime.get("title") or "Unknown"
    title_jp = anime.get("title_japanese") or ""
    synopsis = anime.get("synopsis") or "No synopsis."
    if len(synopsis) > 300:
        synopsis = synopsis[:300].rsplit(" ", 1)[0] + "…"
    score    = anime.get("score") or "N/A"
    episodes = anime.get("episodes") or "?"
    status   = anime.get("status") or "Unknown"
    images   = (anime.get("images") or {}).get("jpg", {})
    image    = images.get("large_image_url") or images.get("image_url") or ""

    embed = discord.Embed(
        title=f"🎌 {title}",
        description=f"*{title_jp}*\n\n{synopsis}",
        url=anime.get("url") or "",
        color=ACCENT
    )
    embed.set_author(name=f'Add to Watchlist?  ·  Search: "{query}"')
    embed.add_field(name="⭐ Score",    value=str(score),                          inline=True)
    embed.add_field(name="📺 Episodes", value=str(episodes),                       inline=True)
    embed.add_field(name="📡 Status",   value=f"{_status_dot(status)} {status}",   inline=True)
    if image:
        embed.set_thumbnail(url=image)
    embed.set_footer(text="React below to confirm — expires in 60 seconds")
    return embed


def _watchlist_embed(entries: list, user: discord.User, page: int, total_pages: int) -> discord.Embed:
    start = page * PAGE_SIZE
    chunk = entries[start : start + PAGE_SIZE]

    embed = discord.Embed(
        title=f"📋 {user.display_name}'s Watchlist",
        description=f"{len(entries)} anime saved  ·  Page {page + 1} / {total_pages}",
        color=ACCENT
    )
    embed.set_thumbnail(url=user.display_avatar.url)

    for i, e in enumerate(chunk, start=start + 1):
        genres = "  ".join(
            f"{GENRE_EMOJIS.get(g, '🎌')} {g}" for g in e.get("genres", [])[:3]
        ) or "—"
        dot    = _status_dot(e.get("status", ""))
        score  = e.get("score", "N/A")
        eps    = e.get("episodes", "?")
        added  = e.get("added_at", "")
        title  = e.get("title", "Unknown")
        url    = e.get("url", "")

        embed.add_field(
            name=f"#{i}  {'[' + title + '](' + url + ')' if url else title}",
            value=(
                f"⭐ `{score}/10`  📺 `{eps} eps`  {dot} `{e.get('status','?')}`\n"
                f"{genres}\n"
                f"{f'Added `{added}`' if added else ''}"
            ),
            inline=False
        )

    embed.set_footer(text="Use /watchlist remove <number> to delete an entry")
    return embed


# ── Confirm / Cancel view ─────────────────────────────────────────────────────

class ConfirmAddView(discord.ui.View):
    def __init__(self, anime: dict, owner_id: int):
        super().__init__(timeout=60)
        self.anime    = anime
        self.owner_id = owner_id
        self.result   = None

    async def _check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "❌ Only the person who ran the command can confirm.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="✅  Add to Watchlist", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check(interaction):
            return
        self.result = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="❌  Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check(interaction):
            return
        self.result = False
        self.stop()
        await interaction.response.defer()


# ── Paginate view ─────────────────────────────────────────────────────────────

class WatchlistPageView(discord.ui.View):
    def __init__(self, entries: list, user: discord.User):
        super().__init__(timeout=120)
        self.entries     = entries
        self.user        = user
        self.page        = 0
        self.total_pages = max(1, (len(entries) + PAGE_SIZE - 1) // PAGE_SIZE)
        self._sync()

    def _sync(self):
        self.prev_btn.disabled = (self.page == 0)
        self.next_btn.disabled = (self.page >= self.total_pages - 1)
        self.counter.label     = f"{self.page + 1} / {self.total_pages}"

    def current_embed(self) -> discord.Embed:
        return _watchlist_embed(self.entries, self.user, self.page, self.total_pages)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self._sync()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    @discord.ui.button(label="1 / 1", style=discord.ButtonStyle.primary, disabled=True)
    async def counter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self._sync()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)


# ── Clear confirm view ────────────────────────────────────────────────────────

class ConfirmClearView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=30)
        self.owner_id = owner_id
        self.result   = None

    async def _check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("❌ Not your watchlist!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🗑️  Yes, clear everything", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check(interaction):
            return
        self.result = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check(interaction):
            return
        self.result = False
        self.stop()
        await interaction.response.defer()


# ── Main Cog ──────────────────────────────────────────────────────────────────

class Watchlist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    wl = discord.app_commands.Group(
        name="watchlist",
        description="📋 Manage your personal anime watchlist"
    )

    # ── /watchlist add ────────────────────────────────────────────────────

    @wl.command(name="add", description="Search for an anime and add it to your watchlist")
    @discord.app_commands.describe(query="Anime title to search for")
    async def wl_add(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(ephemeral=True)

        results = await _search(query)
        if not results:
            await interaction.followup.send(
                f"❌ No results found for **{query}**. Try a different title.", ephemeral=True
            )
            return

        anime = results[0]
        data  = _load()
        uid   = str(interaction.user.id)
        lst   = _user_list(data, uid)

        # Duplicate check
        if any(e.get("mal_id") == anime.get("mal_id") for e in lst):
            title = anime.get("title_english") or anime.get("title") or "Unknown"
            await interaction.followup.send(
                f"⚠️ **{title}** is already in your watchlist!", ephemeral=True
            )
            return

        # Limit check
        if len(lst) >= MAX_PER_USER:
            await interaction.followup.send(
                f"⚠️ Your watchlist is full ({MAX_PER_USER} max). "
                f"Use `/watchlist remove` to make room.", ephemeral=True
            )
            return

        view  = ConfirmAddView(anime, interaction.user.id)
        embed = _confirm_embed(anime, query)
        msg   = await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        await view.wait()

        if view.result is True:
            # Re-load in case another command ran concurrently
            data = _load()
            lst  = _user_list(data, uid)
            if any(e.get("mal_id") == anime.get("mal_id") for e in lst):
                await interaction.followup.send("⚠️ Already added!", ephemeral=True)
                return
            lst.append(_entry_from_anime(anime))
            _save(data)
            title = anime.get("title_english") or anime.get("title") or "Unknown"
            await interaction.followup.send(
                f"✅ **{title}** added to your watchlist! (`#{len(lst)}`)", ephemeral=True
            )
        elif view.result is False:
            await interaction.followup.send("Cancelled.", ephemeral=True)
        else:
            await interaction.followup.send("⏳ Timed out — nothing was added.", ephemeral=True)

    # ── /watchlist view ───────────────────────────────────────────────────

    @wl.command(name="view", description="Browse your anime watchlist")
    async def wl_view(self, interaction: discord.Interaction):
        await interaction.response.defer()

        data = _load()
        uid  = str(interaction.user.id)
        lst  = data.get(uid, [])

        if not lst:
            embed = discord.Embed(
                title="📋 Your Watchlist is Empty",
                description=(
                    "You haven't saved any anime yet!\n\n"
                    "Use `/watchlist add <title>` to get started."
                ),
                color=ACCENT
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
            return

        view  = WatchlistPageView(lst, interaction.user)
        await interaction.followup.send(embed=view.current_embed(), view=view)

    # ── /watchlist remove ─────────────────────────────────────────────────

    @wl.command(name="remove", description="Remove an anime from your watchlist by its number")
    @discord.app_commands.describe(number="The # shown in /watchlist view")
    async def wl_remove(self, interaction: discord.Interaction, number: int):
        await interaction.response.defer(ephemeral=True)

        data = _load()
        uid  = str(interaction.user.id)
        lst  = data.get(uid, [])

        if not lst:
            await interaction.followup.send("📋 Your watchlist is already empty.", ephemeral=True)
            return

        if number < 1 or number > len(lst):
            await interaction.followup.send(
                f"❌ Invalid number. Your watchlist has **{len(lst)}** entries. "
                f"Use a number between 1 and {len(lst)}.", ephemeral=True
            )
            return

        removed = lst.pop(number - 1)
        _save(data)

        await interaction.followup.send(
            f"🗑️ Removed **{removed['title']}** from your watchlist. "
            f"({len(lst)} remaining)",
            ephemeral=True
        )

    # ── /watchlist clear ──────────────────────────────────────────────────

    @wl.command(name="clear", description="Wipe your entire watchlist")
    async def wl_clear(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        data = _load()
        uid  = str(interaction.user.id)
        lst  = data.get(uid, [])

        if not lst:
            await interaction.followup.send("📋 Your watchlist is already empty.", ephemeral=True)
            return

        view = ConfirmClearView(interaction.user.id)
        await interaction.followup.send(
            f"⚠️ This will delete all **{len(lst)} anime** from your watchlist. Are you sure?",
            view=view,
            ephemeral=True
        )

        await view.wait()

        if view.result is True:
            data[uid] = []
            _save(data)
            await interaction.followup.send("🗑️ Your watchlist has been cleared.", ephemeral=True)
        else:
            await interaction.followup.send("Cancelled — nothing was deleted.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Watchlist(bot))
