# classes/managers/SettingsManager.py

from typing import Dict, Any, Optional
from settings.Setting import Setting
from classes.structs.Guild import Guild
from classes.structs.Member import Member
import logging
from shared.types import ExtendedClient


class SettingsManager:
    """
    Manager to handle guild and member settings, integrating with Guild and member classes.
    """

    def __init__(self, client: ExtendedClient, logger: Optional[logging.Logger] = None):
        self.client = client
        self.logger = logger or logging.getLogger("SettingsManager")
        self.guild_manager = client.guild_manager  # Assuming GuildManager is attached to client
        self.member_manager = client.member_manager    # Assuming memberManager is attached to client

    async def load_guild_settings(self, guild_id: int) -> Optional[Guild]:
        """
        Loads settings for a guild and returns a Guild object.
        """
        self.logger.debug(f"Loading settings for guild {guild_id}...")
        guild = await self.guild_manager.fetch_or_create(guild_id)
        if guild:
            self.logger.debug(f"Settings loaded for guild {guild_id}.")
            return guild
        else:
            self.logger.error(f"Failed to load settings for guild {guild_id}.")
            return None

    async def save_guild_setting(self, guild_id: int, setting_id: str, value: Any):
        """
        Saves a specific setting for a guild.
        """
        guild = await self.guild_manager.fetch_or_create(guild_id)
        if not guild:
            raise ValueError(f"Guild with ID {guild_id} not found.")
        
        try:
            await guild.update_setting(setting_id, value)
            self.logger.debug(f"Saved setting '{setting_id}' for guild {guild_id} with value '{value}'.")
        except KeyError as e:
            self.logger.error(str(e))
            raise

    async def load_member_settings(self, member_id: int, guild_id: int) -> Optional[Member]:
        """
        Loads settings for a member within a specific guild and returns a member object.
        """
        self.logger.debug(f"Loading settings for member {member_id} in guild {guild_id}...")
        member_data = await self.member_manager.fetch_or_create(member_id, guild_id)
        if member_data:
            guild = await self.guild_manager.fetch_or_create(guild_id)
            if not guild:
                self.logger.error(f"Guild with ID {guild_id} not found for member {member_id}.")
                return None
            member = Member(
                client=self.client,
                member=guild.guild.get_member(member_id) or await guild.guild.fetch_member(member_id),
                guild=guild,
                settings=member_data.get("settings", {}),
                data=member_data
            )
            self.logger.debug(f"Settings loaded for member {member_id} in guild {guild_id}.")
            return member
        else:
            self.logger.error(f"Failed to load settings for member {member_id} in guild {guild_id}.")
            return None

    async def save_member_setting(self, member_id: int, guild_id: int, setting_id: str, value: Any):
        """
        Saves a specific setting for a member within a guild.
        """
        member = await self.member_manager.fetch_or_create(member_id, guild_id)
        if not member:
            raise ValueError(f"member with ID {member_id} in guild {guild_id} not found.")
        
        try:
            await self.member_manager.update_member(member_id, guild_id, {f"settings.{setting_id}": value})
            self.logger.debug(f"Saved setting '{setting_id}' for member {member_id} in guild {guild_id} with value '{value}'.")
        except Exception as e:
            self.logger.error(f"Error saving setting '{setting_id}' for member {member_id} in guild {guild_id}: {e}")
            raise
        

