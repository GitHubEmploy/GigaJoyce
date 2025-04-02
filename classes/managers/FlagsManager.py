from discord.ext.commands import Bot
from typing import Union, Any
from collections import defaultdict
import logging
from classes.structs.Guild import Guild  # Import explícito para validação


class FlagsManager:
    """
    Manages flags globally and provides utility methods for interacting with guild-specific flags.
    """

    def __init__(self, client: Bot, logger: logging.Logger):
        self.client = client
        self.flags = defaultdict(lambda: None)  # Stores global default flags
        self.logger = logger

    def register_flag(self, flag: str, default_value: Union[str, bool, list]):
        """
        Registers a new flag with a default value.
        """
        if flag in self.flags:
            self.logger.warning(f"Flag {flag} already exists, overwriting it.")
        self.flags[flag] = default_value
        return self

    def delete_flag(self, flag: str):
        """
        Deletes a global flag.
        """
        if flag in self.flags:
            del self.flags[flag]
        return self

    def get_flag(self, guild: Union[Guild, Any], flag: str) -> Any:
        """
        Gets a flag value for a guild, falling back to the global value if not set.
        Ensures that the `guild` is of type `Guild`.
        """
        if not isinstance(guild, Guild):
            self.logger.error(f"Expected a Guild instance, got {type(guild).__name__}.")
            raise TypeError("Invalid guild type.")
        return guild.flags.get(flag) or self.flags.get(flag)

    def has_flag(self, guild: Union[Guild, Any], flag: str) -> bool:
        """
        Checks if a flag is set for a guild or globally.
        Ensures that the `guild` is of type `Guild`.
        """
        if not isinstance(guild, Guild):
            self.logger.error(f"Expected a Guild instance, got {type(guild).__name__}.")
            raise TypeError("Invalid guild type.")
        return guild.flags.has(flag) or flag in self.flags
