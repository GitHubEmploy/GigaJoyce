# classes/structs/SlashCommand.py

import logging
from discord import app_commands
from typing import Callable, Optional, Any

class SlashCommand:
    """
    Represents a Discord slash command with metadata, integrating with discord.app_commands.
    """

    def __init__(
        self,
        data: app_commands.Command,
        func: Optional[Callable[..., Any]] = None,
        global_cmd: bool = False,
        auto_complete_func: Optional[Callable[..., Any]] = None,
        logger: Optional[logging.Logger] = None,
        module: Optional[str] = None,
        disabled: bool = False
    ):
        self.data = data
        self.func = func or data.callback
        self.global_cmd = global_cmd
        self.auto_complete_func = auto_complete_func
        self.logger = logger or logging.getLogger(data.name)
        self.module = module
        self.disabled = disabled

        self.logger.debug(f"Initialized SlashCommand: {data.name}, func: {self.func.__name__}")

    def register_to_tree(self, bot_tree: app_commands.CommandTree):
        """Registers the slash command to the bot's command tree."""
        bot_tree.add_command(self.data)
        self.logger.debug(f"Registered slash command: {self.data.name}")


    @property
    def should_appear_in_help(self) -> bool:
        """Determines if the command should appear in help menus."""
        return self.appears_in_help and not self.disabled
