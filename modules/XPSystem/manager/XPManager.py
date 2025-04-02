# modules/XPSystem/manager/xp_manager.py

from datetime import datetime
from typing import Dict, Any
import logging

class XPManager:
    """
    Manages XP-related logic for the XPSystem module.
    """

    def __init__(self):
        self.logger = logging.getLogger("XPManager")

    async def update_global_xp(self, bot, user_id: str, increment: int):
        """
        Updates the global XP for a user.

        Args:
            bot (commands.Bot): The bot instance.
            user_id (str): The user's ID.
            increment (int): The amount of XP to add.
        """
        # Fetch existing global XP
        data = await bot.db.find_one("XP_Global", {"user_id": user_id}) or {}
        total_xp = data.get("total_xp", 0) + increment
        level = self.calculate_level(total_xp)
        last_updated = datetime.utcnow()

        # Update the database
        await bot.db.update_one(
            "XP_Global",
            {"user_id": user_id},
            {"$set": {
                "total_xp": total_xp,
                "level": level,
                "last_updated": last_updated
            }},
            upsert=True
        )

        self.logger.info(f"Updated global XP for user {user_id}: {total_xp} XP, Level {level}.")

    async def update_local_xp(self, bot, guild_id: str, user_id: str, increment: int):
        """
        Updates the local XP for a user within a guild.

        Args:
            bot (commands.Bot): The bot instance.
            guild_id (str): The guild's ID.
            user_id (str): The user's ID.
            increment (int): The amount of XP to add.
        """
        composite_id = f"{guild_id}_{user_id}"
        data = await bot.db.find_one("XP_Local", {"_id": composite_id}) or {}
        xp = data.get("xp", 0) + increment
        level = self.calculate_level(xp)
        last_updated = datetime.utcnow()

        # Update the database
        await bot.db.update_one(
            "XP_Local",
            {"_id": composite_id},
            {"$set": {
                "xp": xp,
                "level": level,
                "last_updated": last_updated
            }},
            upsert=True
        )

        self.logger.info(f"Updated local XP for user {user_id} in guild {guild_id}: {xp} XP, Level {level}.")

    def calculate_level(self, total_xp: int) -> int:
        """
        Calculates the level based on total XP.

        Args:
            total_xp (int): The user's total XP.

        Returns:
            int: The user's level.
        """
        return total_xp // 1000  # Example: 1000 XP per level

    async def get_user_xp(self, bot, guild_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieves the user's XP data.

        Args:
            bot (commands.Bot): The bot instance.
            guild_id (str): The guild's ID.
            user_id (str): The user's ID.

        Returns:
            Dict[str, Any]: A dictionary containing global and local XP data.
        """
        global_data = await bot.db.find_one("XP_Global", {"user_id": user_id}) or {}
        local_data = await bot.db.find_one("XP_Local", {"_id": f"{guild_id}_{user_id}"}) or {}

        return {
            "global_xp": {
                "total_xp": global_data.get("total_xp", 0),
                "level": global_data.get("level", 0),
                "last_updated": global_data.get("last_updated")
            },
            "local_xp": {
                "xp": local_data.get("xp", 0),
                "level": local_data.get("level", 0),
                "last_updated": local_data.get("last_updated")
            }
        }

    async def cleanup(self):
        """
        Cleanup tasks for the XPManager, if any.
        """
        # Implement any necessary cleanup here
        pass
