# classes/structs/User.py

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional
from discord import Member as DiscordMember
from discord import User as DiscordUser
from collections import defaultdict
from classes.structs.ObjectFlags import ObjectFlags

if TYPE_CHECKING:
    from classes.structs.Guild import Guild
    from settings.Setting import Setting
    from shared.types import ExtendedClient

class Member:
    """
    Represents a Member within a guild, including their data, settings, and flags.
    """

    def __init__(
        self,
        client: ExtendedClient,
        member: Member,
        guild: Guild,
        settings: Dict[str, Setting[Any]],
        data: Dict[str, Any],
    ):
        """
        Initialize the Member object.
        """
        self.id: int = member.id
        self.member: DiscordMember = member
        self.user: DiscordUser = member._user  # Access the Discord User object from Member
        self.client: ExtendedClient = client
        self.data: Dict[str, Any] = data
        self.guild: Guild = guild
        self.settings: Dict[str, Setting[Any]] = defaultdict(lambda: None, settings)
        self.flags: ObjectFlags = ObjectFlags(client, self)

    @property
    def display_name(self) -> str:
        """
        Get the display name of the Member.
        """
        return self.member.display_name if self.member else self.user.name

    def get_setting(self, key: str) -> Optional[Any]:
        """
        Retrieve a specific setting for the member.
        """
        return self.settings.get(key)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a specific setting for the member.
        """
        self.settings[key] = value

    def has_flag(self, flag: str) -> bool:
        """
        Check if the member has a specific flag.
        """
        return self.flags.has(flag)

    def set_flag(self, flag: str, value: Any) -> None:
        """
        Set a flag for the member.
        """
        self.flags.set(flag, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert member data to a dictionary.
        """
        return {
            "id": self.id,
            "name": self.user.name,
            "settings": {key: setting.to_dict() for key, setting in self.settings.items()},
            "flags": self.flags.to_dict(),
        }

    def __repr__(self) -> str:
        """
        Return a string representation of the Member object.
        """
        return f"<Member id={self.id} name={self.user.name} settings={len(self.settings)}>"
