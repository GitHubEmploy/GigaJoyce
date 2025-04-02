from discord.ext.commands import Bot
from typing import Dict, Any
from classes.structs.Permissions import Permissions 
from utils.parsingRelated import parse_from_database
from classes.structs.ObjectFlags import ObjectFlags
from typing import Dict, Any, TYPE_CHECKING
from shared.types import ExtendedClient
from discord import Guild as DiscordGuild

if TYPE_CHECKING:
    from settings.Setting import Setting




class Guild:
    """
    Represents a Discord guild with bot-specific settings and data.
    """

    def __init__(self, client: ExtendedClient, guild: DiscordGuild, guild_data: Dict[str, Any], settings: Dict[str, "Setting"]):
        self.client = client
        self.guild = guild
        self.data = guild_data
        self.settings = settings
        self.permission_overrides = Permissions(client.logger, parse_from_database(guild_data.get("permissions_overrides", [])))
        self.id = guild.id
        self.flags = ObjectFlags(client, self)

    def get_setting(self, setting_id: str) -> "Setting":
        """
        Retrieves a setting by its ID.
        """
        return self.settings.get(setting_id)
