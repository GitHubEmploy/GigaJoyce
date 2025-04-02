from asyncio import sleep
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional
from discord.ext.commands import MissingPermissions
from discord import Embed, Member, NotFound, Object, Webhook, app_commands
from discord.utils import find
from discord.ext.commands import Cog, Greedy, Converter, BucketType, GroupCog
from discord.ext.commands import CheckFailure, BadArgument, MissingRequiredArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions, is_owner, cooldown, hybrid_command
from discord.utils import get
from datetime import datetime, timezone
from collections import defaultdict
import json
import discord
import time



class GuildManager(Cog):
    def __init__(self, bot):
        with open('data/db/emojispersonalizados.json', 'rb') as j:
            self.emojis_personalizados = json.load(j)
        with open('data/db/emojisdefault.json', 'rb') as j:
            self.emojis_padrao = json.load(j)
        with open("data/db/roles.json", 'rb') as f:
            self.role = json.load(f)

        self.bot = bot

    @app_commands.command(name="set_role_xp", description="Set a role with the required XP for a guild")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_role_xp(self, interaction: discord.Interaction, role: discord.Role, xp_required: int):
        """
        Slash command to set the XP required for a role in the guild.
        :param interaction: The context interaction for the command.
        :param role: The role to be set.
        :param xp_required: The XP required to achieve the role.
        """

        await self.bot.db.update_one(
            "role_requirements",
            {"guild_id": interaction.guild.id, "role_id": role.id},
            {
                "$set": {
                    "xp_required": xp_required
                }
            },
            upsert=True  
        )

        await interaction.response.send_message(
            f"Role {role.mention} has been set with a required XP of {xp_required}.", 
            ephemeral=True
        )
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("guild")


async def setup(bot):
    await bot.add_cog(GuildManager(bot))
