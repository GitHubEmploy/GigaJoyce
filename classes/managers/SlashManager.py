import logging
from typing import List
from discord import Client, app_commands, Object
from classes.structs.SlashCommand import SlashCommand

class SlashManager:
    """
    Manages the registration of SlashCommands for the bot.
    """
    def __init__(self, client: Client):
        self.client = client
        self.logger = logging.getLogger("SlashManager")

    async def register_global_commands(self, commands: List[SlashCommand]):
        """
        Register global slash commands.

        Args:
            commands (List[SlashCommand]): A list of slash commands to register globally.
        """
        try:
            if not isinstance(commands, list):
                raise TypeError("Commands must be a list of SlashCommand instances.")

            # Add each slash command to the bot's command tree
            for cmd in commands:
                if not isinstance(cmd, SlashCommand):
                    self.logger.warning(f"Invalid command type: {type(cmd)}. Skipping.")
                    continue
                self.client.tree.add_command(cmd.data)
                self.logger.debug(f"Added global slash command: {cmd.data.name}")

            # Sync the tree globally
            await self.client.tree.sync()
            self.logger.info(f"Registered {len(commands)} global slash commands.")
        except Exception as e:
            self.logger.exception("Failed to register global commands:", exc_info=e)

    async def register_commands_for_guild(self, commands: List[SlashCommand], guild_ids: List[int]):
        """
        Register commands for specific guilds.

        Args:
            commands (List[SlashCommand]): Slash commands to register.
            guild_ids (List[int]): Guild IDs where they will be registered.
        """
        try:
            if not isinstance(commands, list):
                raise TypeError("Commands must be a list of SlashCommand instances.")

            for cmd in commands:
                if not isinstance(cmd, SlashCommand):
                    self.logger.warning(f"Invalid command type: {type(cmd)}. Skipping.")
                    continue
                # Register each command for the specified guilds
                for guild_id in guild_ids:
                    guild = self.client.get_guild(guild_id)
                    if not guild:
                        self.logger.warning(f"Guild with ID {guild_id} not found. Skipping.")
                        continue
                    self.client.tree.add_command(cmd.data, guild=guild)
                    self.logger.debug(f"Added guild-specific slash command: {cmd.data.name} to guild ID: {guild_id}")

            # Sync the tree for each guild
            for guild_id in guild_ids:
                guild = self.client.get_guild(guild_id)
                if guild:
                    await self.client.tree.sync(guild=guild)
                    self.logger.info(f"Registered {len(commands)} slash commands for guild ID {guild_id}.")
        except Exception as e:
            self.logger.exception("Failed to register guild-specific commands:", exc_info=e)
