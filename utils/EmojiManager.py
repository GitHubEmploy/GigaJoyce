import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from logging import Logger


class EmojiManager:
    EMOJI_PATTERN = re.compile(r":([a-zA-Z0-9_]+):")

    def __init__(self, bot, global_path: str, logger: Logger):
        """
        Inicializa o EmojiManager.

        Args:
            bot: Instância do bot.
            global_path (str): Caminho para os emojis globais.
            logger (Logger): Logger para mensagens de depuração e erro.
        """
        self.bot = bot
        self.logger = logger
        self.global_path = Path(global_path)
        self.global_emojis: Dict[str, str] = {}  # Emojis globais
        self.module_emojis: Dict[str, Dict[str, str]] = {}  # Emojis por módulo

    def load_global_emojis(self):
        """
        Carrega os emojis globais a partir do arquivo emoji.json.
        """
        path = self.global_path / "emojis.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                try:
                    self.global_emojis = json.load(f)
                    self.logger.info("Global emojis loaded with success.")
                except json.JSONDecodeError as e:
                    self.logger.error(f"Erro while loading global emojis: {e}")
        else:
            self.logger.warning("File emojis.json wasn't find for global emojis.")

    def load_module_emojis(self, module_name: str, module_path: str):
        """
        Carrega emojis específicos de um módulo.

        Args:
            module_name (str): Nome do módulo.
            module_path (str): Caminho para o módulo.
        """
        path = Path(module_path) / "emojis.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                try:
                    self.module_emojis[module_name] = json.load(f)
                    self.logger.info(f"Emojis loaded with succes for the module: {module_name}")
                except json.JSONDecodeError as e:
                    self.logger.error(f"Erro while loading emojis for the module {module_name}: {e}")
        else:
            self.logger.warning(f"File emojis.json not found for the module: {module_name}")

    def replace_emojis(self, text: str, module_name: Optional[str] = None) -> str:
        """
        Substitui placeholders de emojis no texto com emojis reais.

        Args:
            text (str): Texto com placeholders de emojis.
            module_name (Optional[str]): Nome do módulo (se aplicável).

        Returns:
            str: Texto com emojis substituídos.
        """

        def emoji_replacer(match):
            emoji_name = match.group(1)
            if module_name and module_name in self.module_emojis:
                return self.module_emojis[module_name].get(emoji_name, f":{emoji_name}:")
            return self.global_emojis.get(emoji_name, f":{emoji_name}:")

        return self.EMOJI_PATTERN.sub(emoji_replacer, text)
