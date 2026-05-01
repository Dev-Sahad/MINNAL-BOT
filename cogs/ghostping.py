import discord
from discord.ext import commands
import datetime

class GhostPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Ignore bots and messages with no mentions
        if message.author.bot or not message.mentions:
            return

        # Time check: Only catch it if it was deleted within 60 seconds
        now = datetime.datetime.now(datetime.timezone.utc)
        if (now - message.created_at).total_seconds() > 60:
            return

        # Identify who was pinged
        pinged_users = ", ".join([user.mention for user in message.mentions])

        embed = discord.Embed(
            title="⚡ MINNAL | Ghost Ping Caught!",
            description=f"A message containing a ping was deleted quickly.",
            color=discord.Color.red(),
            timestamp=now
        )
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Pinged Users", value=pinged_users, inline=True)
        embed.add_field(name="Message Content", value=message.content or "[Empty/Attachment]", inline=False)
        embed.set_footer(text="MINNAL Security • Catching shadows")

        # Send the alert to the same channel
        await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GhostPing(bot))
