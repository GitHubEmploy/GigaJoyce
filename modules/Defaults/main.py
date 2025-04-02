from pathlib import Path
from typing import Dict, Any, Callable
from logging import Logger
from discord.ext import commands
from settings.DefaultTypes.select import SelectSetting
from settings.Setting import Setting

def setup(bot: commands.Bot, logger: Logger):
    """
    Initializes the XPSystem module.
    """

    settings = [SelectSetting(
            name="settings.language.name",
            description="settings.language.description",
            id="language",
            options=[
                {"label": "English", "value": "en"},
                {"label": "Português", "value": "pt"},
            ],
            value="en",  # Valor inicial selecionado
            max_values=1,
            min_values=1,
            color="#ffffff",
            module_name="Defaults",
            locales=True
    )]
    return {"settings": settings}