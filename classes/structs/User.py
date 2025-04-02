from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional
from discord import User as DiscordUser
from collections import defaultdict
from classes.structs.ObjectFlags import ObjectFlags

if TYPE_CHECKING:
    from settings.Setting import Setting
    from shared.types import ExtendedClient

class User:
    """
    Represents a Discord user across multiple guilds, including global settings and flags.
    """

    def __init__(
        self,
        client: ExtendedClient,
        user: DiscordUser,
        settings: Dict[str, Setting[Any]],
        data: Dict[str, Any],
    ):
        """
        Initialize the User object.

        Args:
            client (ExtendedClient): The bot client.
            user (DiscordUser): The Discord user object.
            settings (Dict[str, Setting[Any]]): Global settings for the user.
            data (Dict[str, Any]): Additional user-specific data.
        """
        self.id: int = user.id
        self.user: DiscordUser = user
        self.client: ExtendedClient = client
        self.data: Dict[str, Any] = data
        self.settings: Dict[str, Setting[Any]] = defaultdict(lambda: None, settings)
        self.flags: ObjectFlags = ObjectFlags(client, self)

    @property
    def name(self) -> str:
        """
        Get the username of the User.

        Returns:
            str: The username of the user.
        """
        return self.user.name

    @property
    def discriminator(self) -> str:
        """
        Get the discriminator of the User.

        Returns:
            str: The discriminator (e.g., "#1234").
        """
        return self.user.discriminator

    @property
    def display_name(self) -> str:
        """
        Get the display name of the User.

        Returns:
            str: The display name, which is the username in this context.
        """
        return self.user.name

    def get_setting(self, key: str) -> Optional[Any]:
        """
        Retrieve a specific setting for the user.

        Args:
            key (str): The key of the setting to retrieve.

        Returns:
            Optional[Any]: The value of the setting if it exists.
        """
        return self.settings.get(key)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a specific setting for the user.

        Args:
            key (str): The key of the setting to set.
            value (Any): The value to assign to the setting.
        """
        self.settings[key] = value

    def has_flag(self, flag: str) -> bool:
        """
        Check if the user has a specific flag.

        Args:
            flag (str): The flag to check.

        Returns:
            bool: True if the user has the flag, False otherwise.
        """
        return self.flags.has(flag)

    def set_flag(self, flag: str, value: Any) -> None:
        """
        Set a flag for the user.

        Args:
            flag (str): The flag to set.
            value (Any): The value to assign to the flag.
        """
        self.flags.set(flag, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user data to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the user data.
        """
        return {
            "id": self.id,
            "name": self.user.name,
            "settings": {key: setting.to_dict() for key, setting in self.settings.items()},
            "flags": self.flags.to_dict(),
        }

    def __repr__(self) -> str:
        """
        Return a string representation of the User object.

        Returns:
            str: A string representation of the User object.
        """
        return f"<User id={self.id} name={self.user.name} settings={len(self.settings)}>"
