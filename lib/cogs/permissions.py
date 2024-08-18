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
import json
import discord

class PermissionManager(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_permission", description="Set additional permissions for a role")
    @app_commands.choices(permission=[
        app_commands.Choice(name="Ban", value="ban"),
        app_commands.Choice(name="Kick", value="kick"),
        app_commands.Choice(name="Mute", value="mute")
    ])
    @app_commands.choices(value=[
        app_commands.Choice(name="Grant", value="True"),
        app_commands.Choice(name="Revoke", value="False"),
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def set_permission(self, interaction: discord.Interaction, role: discord.Role, permission: str, value: str):
        """
        Command to set additional permissions for a role.
        :param interaction: Discord Interaction object.
        :param role: The role for which the permission will be set.
        :param permission: The permission to be set ('ban', 'kick', 'mute').
        :param value: Whether to grant or revoke the permission (True to grant, False to revoke).
        """

        # Convert string value to boolean
        value = value == "True"

        # Map the permission string to the corresponding database field
        permission_fields = {
            "ban": "ban_permission",
            "kick": "kick_permission",
            "mute": "mute_permission"
        }

        if permission not in permission_fields:
            await interaction.response.send_message(
                f"Invalid permission: `{permission}`. Valid permissions are {', '.join(permission_fields.keys())}.",
                ephemeral=True)
            return

        # Update or insert the permission in the database
        await self.bot.db.update_one(
            "roles",  # This is the collection name
            {"guild_id": interaction.guild.id, "role_id": role.id},
            {permission_fields[permission]: value},
            upsert=True
        )

        action = "granted" if value else "revoked"
        await interaction.response.send_message(f"Permission `{permission}` has been {action} for role `{role.name}`.", ephemeral=True)

    @app_commands.command(name="get_permissions", description="Get the current permissions of a role")
    @app_commands.checks.has_permissions(administrator=True)
    async def get_permissions(self, interaction: discord.Interaction, role: discord.Role):
        """
        Command to get the current permissions of a role.
        :param interaction: Discord Interaction object.
        :param role: The role for which the permissions will be retrieved.
        """

        # Retrieve the role's permissions from the database
        role_permissions = await self.bot.db.find_one({"guild_id": interaction.guild.id, "role_id": role.id})

        if role_permissions:
            permissions = {
                "ban": role_permissions.get("ban_permission", False),
                "kick": role_permissions.get("kick_permission", False),
                "mute": role_permissions.get("mute_permission", False)
            }

            embed = discord.Embed(
                title=f"Permissions for Role: {role.name}",
                description="\n".join([f"**{perm.capitalize()}:** {value}" for perm, value in permissions.items()]),
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"No permissions found for role `{role.name}`.", ephemeral=True)
            
            
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("permissions")


async def setup(bot):
    await bot.add_cog(PermissionManager(bot))
