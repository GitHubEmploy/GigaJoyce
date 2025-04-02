import discord
from discord.ext import commands
from discord import app_commands
from pathlib import Path
from shared.types import ExtendedClient
from typing import Optional


class OwnerCommands(commands.Cog):
    def __init__(self, bot: ExtendedClient):
        self.bot = bot

    @staticmethod
    def is_owner(interaction: discord.Interaction) -> bool:
        """
        Check if the user executing the command is the bot owner.
        """
        print(f"Owner: {interaction.client.owner_ids}")
        return interaction.user.id in interaction.client.owner_ids

    async def reload_module(self, module_name: str, sync: Optional[str] = None, guild_id: Optional[str] = None):
        """
        Helper function to reload a module with optional sync and guild ID.
        """
        if module_name not in self.bot.modules:
            return f"Module '{module_name}' not found."

        module = self.bot.modules[module_name]
        try:
            await module.reload(bot=self.bot, sync=sync, guild_id=guild_id)
            return f"Module '{module_name}' reloaded successfully."
        except Exception as e:
            return f"Failed to reload module '{module_name}': {e}"

    async def unload_module(self, module_name: str, sync: Optional[str] = None, guild_id: Optional[str] = None):
        """
        Helper function to unload a module.
        """
        if module_name not in self.bot.modules:
            return f"Module '{module_name}' not found."

        module = self.bot.modules[module_name]
        try:
            await module.unload(bot=self.bot, guild_id=guild_id, sync=sync)
            del self.bot.modules[module_name]
            return f"Module '{module_name}' unloaded successfully."
        except Exception as e:
            return f"Failed to unload module '{module_name}': {e}"

    async def load_module(self, module_name: str, sync: Optional[str] = None, guild_id: Optional[str] = None):
        """
        Helper function to load a module with optional sync and guild ID.
        """
        module_path = Path(f"./modules/{module_name}")
        if not module_path.exists():
            return f"Module '{module_name}' not found in the modules directory."

        try:
            await self.bot.module_handler.load_modules(specific_module=module_name)
            if module_name in self.bot.modules:
                if sync:
                    await self.sync_commands(sync, guild_id)
                return f"Module '{module_name}' loaded successfully."
            return f"Failed to load module '{module_name}'."
        except Exception as e:
            return f"Failed to load module '{module_name}': {e}"

    async def sync_commands(self, sync: str, guild_id: Optional[str]):
        """
        Helper function to sync commands globally or for a specific guild.
        """
        if sync == "global":
            await self.bot.tree.sync()
            return "Commands synced globally."
        elif sync == "guild" and guild_id:
            guild = discord.Object(id=int(guild_id))
            await self.bot.tree.sync(guild=guild)
            return f"Commands synced to guild ID {guild_id}."
        return "No synchronization performed."

    @app_commands.command(name="module_reload", description="Reload a module (owner only).")
    @app_commands.check(is_owner)
    async def module_reload(
        self,
        interaction: discord.Interaction,
        module_name: str,
        sync: Optional[str] = None,
        guild_id: Optional[str] = None
    ):
        """
        Slash command to reload a module.
        """
        result = await self.reload_module(module_name, sync=sync, guild_id=guild_id)
        await interaction.response.send_message(result, ephemeral=True)

    @app_commands.command(name="module_unload", description="Unload a module (owner only).")
    @app_commands.check(is_owner)
    async def module_unload(
        self,
        interaction: discord.Interaction,
        module_name: str,
        sync: Optional[str] = None,
        guild_id: Optional[str] = None
    ):
        """
        Slash command to unload a module.
        """
        if module_name not in self.bot.modules:
            await interaction.response.send_message(f"Module '{module_name}' not found.", ephemeral=True)
            return

        result = await self.unload_module(self.bot, sync=sync, guild_id=guild_id)
        await interaction.response.send_message(result, ephemeral=True)


    @app_commands.command(name="module_load", description="Load a module (owner only).")
    @app_commands.check(is_owner)
    async def module_load(
        self,
        interaction: discord.Interaction,
        module_name: str,
        sync: Optional[str] = None,
        guild_id: Optional[str] = None
    ):
        """
        Slash command to load a module.
        """
        result = await self.load_module(module_name, sync=sync, guild_id=guild_id)
        await interaction.response.send_message(result, ephemeral=True)

    @module_reload.error
    @module_unload.error
    @module_load.error
    async def command_error(self, interaction: discord.Interaction, error):
        """
        Handles errors for module management commands.
        """
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "This command is restricted to the bot owner.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"An error occurred: {error}", ephemeral=True
            )


exports = [OwnerCommands]
