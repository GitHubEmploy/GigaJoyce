# classes/structs/Settings.py

from typing import Any, Dict, Callable, Awaitable, Optional
from dataclasses import dataclass
import logging

@dataclass
class Setting:
    """
    Represents a setting with metadata and value.
    """
    name: str
    description: str
    id: str
    type: str
    permission: Optional[int] = None
    color: Optional[str] = None
    run: Optional[Callable[[Any], Awaitable[Any]]] = None
    save: Optional[Callable[['Bot', int, 'Setting'], Awaitable[bool]]] = None
    load: Optional[Callable[['Bot', Any, Any], Awaitable[Any]]] = None
    value: Any = None

    def clone(self) -> 'Setting':
        """
        Creates a copy of the setting.
        """
        return Setting(
            name=self.name,
            description=self.description,
            id=self.id,
            type=self.type,
            permission=self.permission,
            color=self.color,
            run=self.run,
            save=self.save,
            load=self.load,
            value=self.value
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the setting to a dictionary.
        """
        return {
            "name": self.name,
            "description": self.description,
            "id": self.id,
            "type": self.type,
            "permission": self.permission,
            "value": self.value,
            "color": self.color,
        }


async def default_save_method(bot: 'Bot', entity_id: int, setting: Setting) -> bool:
    """
    Default method to save the value of a setting to the database.
    """
    try:
        if hasattr(bot, 'logger'):
            bot.logger.debug(f"Saving setting '{setting.id}' with value '{setting.value}' for entity {entity_id}.")

        if hasattr(bot, 'db'):
            collection = "guilds" if isinstance(entity_id, int) else "users"
            key = "guild_id" if isinstance(entity_id, int) else "user_id"
            await bot.db.update_one(
                collection,
                {key: str(entity_id)},
                {"$set": {f"settings.{setting.id}.value": setting.value}},
                upsert=True,
            )
            return True
        raise ValueError("Database connection not available.")
    except Exception as e:
        if hasattr(bot, "logger"):
            bot.logger.error(f"Error saving setting '{setting.id}': {e}")
        return False
