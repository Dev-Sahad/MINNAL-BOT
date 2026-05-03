# =============================================================================
#  cogs/log_relay.py — Railway Log Relay → Discord Channel
#  Fetches Railway deployment logs every 5 minutes and posts new ones to Discord
# =============================================================================

import discord
from discord.ext import commands, tasks
import asyncio
import os
import json
import time
import requests

LOG_CHANNEL_ID = 1499449737047314543

RAILWAY_API    = "https://backboard.railway.app/graphql/v2"
SERVICE_ID     = "9ec71862-e3e9-4b72-8824-107807cd974c"
ENVIRONMENT_ID = "f51434f3-fa8e-4da8-8e06-a05d1f82c78f"

STATE_FILE = "data/log_relay_state.json"

# Max log lines per Discord message
CHUNK_SIZE = 30


def _railway_query(query: str, variables: dict) -> dict:
    token = os.getenv("RAILWAY_API_TOKEN", "")
    if not token:
        raise RuntimeError("RAILWAY_API_TOKEN not set")
    r = requests.post(
        RAILWAY_API,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"query": query, "variables": variables},
        timeout=15
    )
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"][0]["message"])
    return data.get("data", {})


def _get_latest_deployment_id() -> str:
    data = _railway_query(
        """query($serviceId: String!, $environmentId: String!) {
          serviceInstance(serviceId: $serviceId, environmentId: $environmentId) {
            latestDeployment { id status }
          }
        }""",
        {"serviceId": SERVICE_ID, "environmentId": ENVIRONMENT_ID}
    )
    dep = data.get("serviceInstance", {}).get("latestDeployment", {})
    if not dep or not dep.get("id"):
        raise RuntimeError("No deployment found")
    return dep["id"]


def _get_logs(deployment_id: str, limit: int = 150) -> list:
    data = _railway_query(
        """query($deploymentId: String!, $limit: Int!) {
          deploymentLogs(deploymentId: $deploymentId, limit: $limit) {
            timestamp message severity
          }
        }""",
        {"deploymentId": deployment_id, "limit": limit}
    )
    raw = data.get("deploymentLogs", []) or []
    # Strip ANSI codes
    import re
    ansi = re.compile(r'\x1b\[[0-9;]*m')
    return [
        {
            "timestamp": l["timestamp"],
            "message":   ansi.sub("", l["message"]).strip(),
            "severity":  (l.get("severity") or "INFO").upper()
        }
        for l in raw
        if l.get("message", "").strip()
    ]


def _load_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {"last_timestamp": "", "deployment_id": ""}


def _save_state(state: dict):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def _severity_color(sev: str) -> int:
    return {
        "ERROR": 0xe74c3c,
        "WARN":  0xf39c12,
        "WARNING": 0xf39c12,
        "INFO": 0x7c5cfc,
        "DEBUG": 0x7a7a9a,
    }.get(sev, 0x5c9afc)


def _severity_icon(sev: str) -> str:
    return {
        "ERROR": "🔴",
        "WARN":  "🟡",
        "WARNING": "🟡",
        "INFO":  "🟣",
        "DEBUG": "⚫",
    }.get(sev, "⚪")


class LogRelay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.state = _load_state()
        self.relay_task.start()
        pass  # startup logged by discord_bot.py

    def cog_unload(self):
        self.relay_task.cancel()

    @tasks.loop(minutes=5)
    async def relay_task(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if channel is None:
            print(f"📡 [LogRelay] Channel {LOG_CHANNEL_ID} not found", flush=True)
            return

        try:
            # Run blocking Railway API call in executor
            loop = asyncio.get_event_loop()
            dep_id = await loop.run_in_executor(None, _get_latest_deployment_id)

            # Reset state if new deployment
            if dep_id != self.state.get("deployment_id"):
                self.state["deployment_id"] = dep_id
                self.state["last_timestamp"] = ""

            logs = await loop.run_in_executor(None, lambda: _get_logs(dep_id, 150))

            last_ts = self.state.get("last_timestamp", "")
            new_logs = [l for l in logs if l["timestamp"] > last_ts] if last_ts else logs[-20:]

            if not new_logs:
                return

            # Update state
            self.state["last_timestamp"] = max(l["timestamp"] for l in new_logs)
            _save_state(self.state)

            # Determine if there are any errors/warnings for embed colour
            has_error = any(l["severity"] in ("ERROR",) for l in new_logs)
            has_warn  = any(l["severity"] in ("WARN", "WARNING") for l in new_logs)
            color = 0xe74c3c if has_error else (0xf39c12 if has_warn else 0x7c5cfc)

            # Post in chunks
            for i in range(0, len(new_logs), CHUNK_SIZE):
                chunk = new_logs[i:i + CHUNK_SIZE]

                lines = []
                for l in chunk:
                    icon  = _severity_icon(l["severity"])
                    ts    = l["timestamp"][11:19] if len(l["timestamp"]) >= 19 else l["timestamp"]
                    msg   = l["message"][:200]
                    lines.append(f"`{ts}` {icon} {msg}")

                body = "\n".join(lines)
                if len(body) > 3900:
                    body = body[:3900] + "\n…"

                is_first = (i == 0)
                embed = discord.Embed(
                    title="⚡ MINNAL Railway Logs" if is_first else None,
                    description=body,
                    color=color,
                    timestamp=discord.utils.utcnow()
                )
                if is_first:
                    embed.set_footer(text=f"🚂 Railway · {len(new_logs)} new line(s) · Deployment {dep_id[:8]}…")

                await channel.send(embed=embed)

            print(f"📡 [LogRelay] Sent {len(new_logs)} new log line(s) to #{channel.name}", flush=True)

        except Exception as e:
            print(f"📡 [LogRelay] Error: {e}", flush=True)
            try:
                channel = self.bot.get_channel(LOG_CHANNEL_ID)
                if channel:
                    embed = discord.Embed(
                        title="⚠️ Log Relay Error",
                        description=f"```{str(e)[:500]}```",
                        color=0xe74c3c,
                        timestamp=discord.utils.utcnow()
                    )
                    await channel.send(embed=embed)
            except Exception:
                pass

    @relay_task.before_loop
    async def before_relay(self):
        await self.bot.wait_until_ready()
        # Wait 30s after startup before first fetch
        await asyncio.sleep(30)

    @discord.app_commands.command(name="relay_now", description="Manually fetch and relay Railway logs now")
    async def relay_now(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admins only.", ephemeral=True)
            return
        await interaction.response.send_message("⏳ Fetching logs...", ephemeral=True)
        await self.relay_task()
        await interaction.edit_original_response(content="✅ Logs relayed!")


async def setup(bot: commands.Bot):
    await bot.add_cog(LogRelay(bot))
