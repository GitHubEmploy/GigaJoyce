import os
import json
from pathlib import Path
from discord.ext import commands
from logging import Logger
from typing import Dict
import logging

async def load_commands_from_folder(bot: commands.Bot, folder: Path, base_package: str, logger: Logger):
    """
    Dynamically loads commands from a specified folder.
    
    :param bot: The bot instance.
    :param folder: The Path object for the folder containing command files.
    :param base_package: The base Python package path to use when loading extensions.
    :param logger: Logger instance for logging progress and errors.
    """
    if not folder.exists():
        logger.warning(f"Commands folder '{folder}' does not exist.")
        return

    for command_file in folder.glob("*.py"):
        if command_file.stem.startswith("_"):
            # Skip private or special files like __init__.py
            continue

        extension = f"{base_package}.{command_file.stem}"
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded command: {command_file.stem}")
        except Exception as e:
            logger.error(f"Failed to load command '{command_file.stem}': {e}")
            


def load_translation(module_name: str, file_name: str, language: str, default_language: str = "en") -> Dict:
    """
    Carrega o dicionário de traduções baseado no idioma fornecido.

    Args:
        module_name (str): Nome do módulo onde estão as traduções (e.g., "XPSystem").
        file_name (str): Nome do arquivo de tradução (sem extensão .json).
        language (str): Idioma preferido da guilda.
        default_language (str): Idioma padrão caso o preferido não esteja disponível.

    Returns:
        Dict: Dicionário de traduções no idioma solicitado.

    Raises:
        FileNotFoundError: Se o arquivo de tradução não existir.
        ValueError: Se o JSON não puder ser decodificado ou se o idioma não estiver disponível.
    """
    logger = logging.getLogger("TranslationLoader")
    translations_path = Path(f"modules/{module_name}/translations/{file_name}.json")

    if not translations_path.exists():
        logger.error(f"Translation file '{translations_path}' not found.")
        raise FileNotFoundError(f"Translation file '{translations_path}' not found.")

    try:
        with open(translations_path, "r", encoding="utf-8") as file:
            translations = json.load(file)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file '{translations_path}': {e}")
        raise ValueError(f"Error decoding JSON file '{translations_path}': {e}")

    if language not in translations and default_language not in translations:
        logger.error(f"Language '{language}' and default language '{default_language}' not found in '{translations_path}'.")
        raise ValueError(f"Language '{language}' and default language '{default_language}' not found in '{translations_path}'.")

    logger.debug(f"Successfully loaded translations for language '{language}' from '{translations_path}'.")
    return translations.get(language, translations.get(default_language))

