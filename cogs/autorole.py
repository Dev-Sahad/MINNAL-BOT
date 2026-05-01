import discord
from discord.ext import commands

# --- SETTINGS ---
# Replace with your actual Role IDs
UNVERIFIED_ROLE_ID = 1499465138011504692  # Role for new joiners
VERIFIED_ROLE_ID = 1499465467402653767      # Sxhd's fam [verified]

class MinnalAutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Automatically assigns the Unverified role when someone joins"""
        role = member.guild.get_role(UNVERIFIED_ROLE_ID)
        
        if role:
            try:
                await member.add_roles(role)
                print(f"⚡ MINNAL assigned {role.name} to {member.name}")
            except discord.Forbidden:
                print("❌ MINNAL lacks permission to assign roles. Move my role higher!")
            except Exception as e:
                print(f"❌ Error assigning role: {e}")
        else:
            print("❌ Unverified Role ID not found in server.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Optional: If they get the Verified role, 
        MINNAL can automatically remove the Unverified role.
        """
        unverified_role = after.guild.get_role(UNVERIFIED_ROLE_ID)
        verified_role = after.guild.get_role(VERIFIED_ROLE_ID)

        # Check if they just received the Verified role
        if verified_role not in before.roles and verified_role in after.roles:
            if unverified_role in after.roles:
                try:
                    await after.remove_roles(unverified_role)
                    print(f"⚡ MINNAL removed Unverified role from {after.name} (Verified)")
                except:
                    pass

async def setup(bot):
    await bot.add_cog(MinnalAutoRole(bot))
