from typing import Dict, Any, Optional
from settings.setting import ConcreteSetting
from discord.ext.commands import Bot
import logging

class SettingsHandler:
    """
    Handler to manage guild and user settings.
    """

    def __init__(self, bot: Bot, logger: Optional[logging.Logger] = None):
        self.bot = bot
        self.logger = logger or logging.getLogger("SettingsHandler")
        self.guild_settings: Dict[int, Dict[str, ConcreteSetting]] = {}
        self.user_settings: Dict[int, Dict[str, ConcreteSetting]] = {}

    async def load_settings(self, guild_id: int) -> Dict[str, ConcreteSetting]:
        """
        Load settings for a guild from the database.
        """
        data = await self.bot.db.find_one("guilds", {"guild_id": str(guild_id)}) or {}
        settings = {
            key: ConcreteSetting(**value) for key, value in data.get("settings", {}).items()
        }
        self.guild_settings[guild_id] = settings
        return settings

    async def save_setting(self, guild_id: int, setting_id: str, value: Any):
        """
        Save a setting's value to the database.
        """
        if guild_id not in self.guild_settings or setting_id not in self.guild_settings[guild_id]:
            raise ValueError("Setting not found.")
        self.guild_settings[guild_id][setting_id].value = value
        await self.bot.db.update_one(
            "guilds",
            {"guild_id": str(guild_id)},
            {"$set": {f"settings.{setting_id}.value": value}},
            upsert=True,
        )

    def get_setting(self, guild_id: int, setting_id: str) -> Optional[ConcreteSetting]:
        """
        Retrieve a setting for a guild.
        """
        return self.guild_settings.get(guild_id, {}).get(setting_id)

    async def register_setting(self, guild_id: int, setting: ConcreteSetting):
        """
        Register a new setting for a guild.
        """
        if guild_id not in self.guild_settings:
            await self.load_settings(guild_id)
        self.guild_settings[guild_id][setting.id] = setting
        await self.save_setting(guild_id, setting.id, setting.value)

    async def set_language(self, guild_id: int, language: str):
        """
        Define o idioma da guilda.

        Args:
            guild_id (int): ID da guilda.
            language (str): Código do idioma (e.g., 'en', 'pt').
        """
        try:
            await self.save_setting(guild_id, "language", language)
            self.logger.info(f"Set language for guild {guild_id} to {language}.")
        except ValueError as e:
            self.logger.error(f"Error setting language for guild {guild_id}: {e}")

    def get_language(self, guild_id: int) -> str:
        """
        Retorna o idioma configurado para a guilda. Padrão é 'en' se não estiver configurado.

        Args:
            guild_id (int): ID da guilda.

        Returns:
            str: Código do idioma.
        """
        setting = self.get_setting(guild_id, "language")
        return setting.value if setting else "en"  # Default para inglês
