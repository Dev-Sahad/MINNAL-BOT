# =============================================================================
#  cogs/ai_chat.py — AI Chat Channel powered by Claude
#  Powered by Replit AI Integrations (no API key needed)
#
#  Set  data/settings.json → ai_chat → channel_id  to activate.
#  Every message in that channel gets a Claude response.
#  Each user has their own conversation history (last 20 messages).
#  /aiclear  resets your personal conversation history.
# =============================================================================

import discord
from discord.ext import commands
import os
import json
import asyncio
from collections import defaultdict
import logger as log

SETTINGS_FILE   = "data/settings.json"
MAX_HISTORY     = 20    # messages kept per user (10 exchanges)
MAX_RESPONSE    = 1900  # Discord hard limit is 2000; leave headroom
TYPING_INTERVAL = 8     # seconds between keep-alive typing bursts

SYSTEM_PROMPT = (
    "You are MINNAL, a powerful AI assistant living inside a Discord server. "
    "You are deeply knowledgeable about anime, manga, gaming, and pop culture, "
    "but you can help with absolutely anything — code, questions, creative writing, "
    "debates, and more.\n\n"
    "Personality:\n"
    "- Energetic and friendly, with an anime-enthusiast soul\n"
    "- Use Discord markdown (bold, italics, code blocks) when it improves clarity\n"
    "- Keep answers concise for simple questions, thorough for complex ones\n"
    "- When talking about anime, show genuine excitement and knowledge\n"
    "- Never break character as MINNAL\n\n"
    "You are powered by Claude via Replit AI Integrations."
)


def _load_settings() -> dict:
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _get_channel_id() -> int | None:
    s = _load_settings()
    cid = (s.get("ai_chat") or {}).get("channel_id")
    if cid:
        try:
            return int(cid)
        except ValueError:
            pass
    return None


def _make_client():
    """Build Anthropic client using Replit AI Integration env vars."""
    from anthropic import Anthropic
    base_url = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")
    api_key  = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY", "replit-proxy")
    if not base_url:
        raise RuntimeError("AI_INTEGRATIONS_ANTHROPIC_BASE_URL not set")
    return Anthropic(api_key=api_key, base_url=base_url)


def _split_message(text: str, limit: int = MAX_RESPONSE) -> list[str]:
    """Split a long response into Discord-safe chunks."""
    if len(text) <= limit:
        return [text]
    chunks, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > limit:
            if current:
                chunks.append(current.rstrip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        chunks.append(current.rstrip())
    return chunks or [text[:limit]]


# ── Main Cog ──────────────────────────────────────────────────────────────────

class AIChat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot      = bot
        self.history: dict[int, list[dict]] = defaultdict(list)  # user_id → messages
        try:
            self.client = _make_client()
            log.event("ai_chat", "Claude client ready via Replit AI Integrations")
        except RuntimeError as e:
            self.client = None
            log.error("ai_chat", str(e))

    # ── Listen for messages in the AI channel ─────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        channel_id = _get_channel_id()
        if not channel_id or message.channel.id != channel_id:
            return
        if not self.client:
            await message.reply("⚠️ AI is not configured yet. Ask an admin to set it up.")
            return

        content = message.content.strip()
        if not content:
            return

        # Add user message to history
        uid = message.author.id
        self.history[uid].append({"role": "user", "content": content})
        # Keep only last MAX_HISTORY messages
        if len(self.history[uid]) > MAX_HISTORY:
            self.history[uid] = self.history[uid][-MAX_HISTORY:]

        # Show typing indicator and call Claude
        async with message.channel.typing():
            try:
                response_text = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._call_claude(uid)
                )
            except Exception as e:
                log.error("ai_chat", f"Claude error: {e}")
                await message.reply(
                    "⚠️ Something went wrong. Please try again in a moment.",
                    mention_author=False
                )
                # Roll back the failed message so history stays clean
                if self.history[uid]:
                    self.history[uid].pop()
                return

        # Add assistant reply to history
        self.history[uid].append({"role": "assistant", "content": response_text})
        if len(self.history[uid]) > MAX_HISTORY:
            self.history[uid] = self.history[uid][-MAX_HISTORY:]

        # Send response (split if too long)
        chunks = _split_message(response_text)
        first  = True
        for chunk in chunks:
            if first:
                await message.reply(chunk, mention_author=False)
                first = False
            else:
                await message.channel.send(chunk)

        log.event("ai_chat", f"{message.author} — {len(response_text)} chars")

    def _call_claude(self, uid: int) -> str:
        """Synchronous Claude call (run in executor to avoid blocking the event loop)."""
        resp = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=self.history[uid],
        )
        block = resp.content[0] if resp.content else None
        return block.text if block and block.type == "text" else "…"

    # ── /aiclear — reset your conversation history ────────────────────────

    @discord.app_commands.command(
        name="aiclear",
        description="Reset your AI conversation history in the chat channel"
    )
    async def aiclear(self, interaction: discord.Interaction):
        uid = interaction.user.id
        count = len(self.history.get(uid, []))
        self.history[uid] = []
        if count:
            await interaction.response.send_message(
                f"🧹 Cleared your conversation history ({count} messages). "
                f"Fresh start!", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "📭 Your history was already empty.", ephemeral=True
            )
        log.event("ai_chat", f"{interaction.user} cleared history ({count} msgs)")

    # ── /aiping — quick sanity check ─────────────────────────────────────

    @discord.app_commands.command(
        name="aiping",
        description="Check if the AI chat is active and which channel it's watching"
    )
    async def aiping(self, interaction: discord.Interaction):
        channel_id = _get_channel_id()
        if not channel_id:
            await interaction.response.send_message(
                "⚠️ No AI chat channel is configured yet.\n"
                "Set `ai_chat.channel_id` in `data/settings.json`.",
                ephemeral=True
            )
            return
        channel = self.bot.get_channel(channel_id)
        name    = f"<#{channel_id}>" if channel else f"ID `{channel_id}` (not found)"
        status  = "✅ Claude ready" if self.client else "❌ Client not initialized"
        await interaction.response.send_message(
            f"**AI Chat Status**\n"
            f"Channel : {name}\n"
            f"Engine  : Claude (Replit AI Integrations)\n"
            f"Status  : {status}",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AIChat(bot))
