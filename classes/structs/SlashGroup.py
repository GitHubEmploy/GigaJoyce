# classes/structs/SlashGroup.py

import logging
from discord import app_commands
from typing import Optional

class SlashGroup:
    """
    Represents a group of slash commands, integrating with app_commands.Group.
    """

    def __init__(
        self,
        group: app_commands.Group,
        global_cmd: bool = False,
        logger: Optional[logging.Logger] = None,
        module: Optional[str] = None,
        disabled: bool = False
    ):
        self.group = group
        self.global_cmd = global_cmd
        self.logger = logger or logging.getLogger(group.name)
        self.module = module
        self.disabled = disabled

        self.logger.debug(f"Initialized SlashGroup: {group.name}")

    def add_subcommand(self, command: app_commands.Command):
        """Adds a subcommand to the group."""
        self.group.add_command(command)
        self.logger.debug(f"Added subcommand {command.name} to group {self.group.name}")

    def register_to_tree(self, bot_tree: app_commands.CommandTree):
        """Registers the group to the bot's command tree."""
        bot_tree.add_command(self.group)
        self.logger.debug(f"Registered group '{self.group.name}' to command tree.")
