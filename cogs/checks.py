# =============================================================================
#  cogs/checks.py — Shared app_commands check decorators
# =============================================================================

import discord
from discord import app_commands
import config


def is_admin():
    """
    Custom check for admin-only slash commands.
    Passes if the user is:
      - in config.DEVELOPER_IDS (bot developer bypass)
      - the guild owner
      - a member with the Administrator permission
    Works correctly even when Discord's integration overrides are in effect.
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            raise app_commands.CheckFailure("This command can only be used inside a server.")
        user_id = interaction.user.id
        if user_id in config.DEVELOPER_IDS:
            return True
        if interaction.guild.owner_id == user_id:
            return True
        member = interaction.guild.get_member(user_id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(user_id)
            except Exception:
                raise app_commands.MissingPermissions(["administrator"])
        if member.guild_permissions.administrator:
            return True
        raise app_commands.MissingPermissions(["administrator"])
    return app_commands.check(predicate)
