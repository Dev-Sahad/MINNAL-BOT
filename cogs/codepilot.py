# =============================================================================
#  cogs/codepilot.py — CodePilot AI Assistant
#  Adds /ask command to interact with CodePilot AI directly from Discord
# =============================================================================

import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import config

class CodePilot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ask", description="Ask CodePilot AI a coding question or get help with MINNAL-BOT")
    @app_commands.describe(question="Your coding question or request")
    async def ask(self, interaction: discord.Interaction, question: str):
        # Only allow staff or developer to use this command
        staff_role = interaction.guild.get_role(config.STAFF_ROLE_ID)
        is_staff = staff_role in interaction.user.roles if staff_role else False
        is_dev = interaction.user.id in config.DEVELOPER_IDS

        if not (is_staff or is_dev):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are CodePilot, a coding assistant specialized in Python Discord bots. "
                                "You help with bug fixing, feature ideas, and code improvements for MINNAL-BOT. "
                                "Be concise and practical. Show code when relevant."
                            )
                        },
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 800
                }

                headers = {
                    "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }

                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers
                ) as resp:
                    data = await resp.json()

                    if resp.status != 200:
                        await interaction.followup.send(
                            f"⚠️ API error: {data.get('error', {}).get('message', 'Unknown error')}"
                        )
                        return

                    answer = data["choices"][0]["message"]["content"]

        except Exception as e:
            await interaction.followup.send(f"❌ Something went wrong: `{e}`")
            return

        # Split long responses into chunks
        if len(answer) > 1900:
            chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
            embed = discord.Embed(
                title="🤖 CodePilot Response",
                description=chunks[0],
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"Asked by {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)
            for chunk in chunks[1:]:
                await interaction.followup.send(f"```{chunk}```")
        else:
            embed = discord.Embed(
                title="🤖 CodePilot Response",
                description=answer,
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"Asked by {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="codepilot", description="Show CodePilot status and available commands")
    async def codepilot_info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 CodePilot AI Assistant",
            description="Your in-server coding assistant for MINNAL-BOT!",
            color=discord.Color.blurple()
        )
        embed.add_field(name="/ask [question]", value="Ask any coding question or request a fix", inline=False)
        embed.add_field(name="/codepilot", value="Show this info panel", inline=False)
        embed.set_footer(text="Powered by CodePilot • Base44")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(CodePilot(bot))
