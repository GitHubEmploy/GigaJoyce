import json
from pathlib import Path
from typing import Dict, Any, Callable, Optional

import aiofiles
from shared.types import ExtendedClient
from collections import defaultdict
import logging
from pathlib import Path

# class Translator:
#     def __init__(self, bot: ExtendedClient, global_path: str, logger: logging.Logger):
#         self.bot = bot
#         self.logger = logger
#         self.global_path = global_path
#         self.global_translations_cache = {}
#         self.language_cache = {}
#         self.module_translation_cache = {}

#     async def get_language(self, guild_id: str) -> str:
#         """
#         Retorna o idioma configurado para uma guild. Padrão: 'en'.
#         Atualiza o cache local quando necessário.
#         """
#         # Verifica o cache primeiro
#         guild_id = str(guild_id)
#         if guild_id in self.language_cache:
#             self.logger.info(f"Found {guild_id} in cache: {self.language_cache[guild_id]}")
#             return self.language_cache[guild_id]

#         # Busca o idioma no banco de dados
#         guild = await self.bot.guild_manager.fetch_or_create(guild_id)

#         language = guild.data.get("language", "en")
        
#         if language in ["Inglês", "English", "en", "en-US"]:
#             self.language_cache[guild_id] = "en"
#             language = "en"
#         elif language in ["Português", "pt-br", "Português (Brasileiro)", "pt"]:
#             self.language_cache[guild_id] = "pt"
#             language = "pt"
#         else:
#             self.language_cache[guild_id] = language
#         return language
    
#     def get_language_sync(self, guild_id: Optional[str]) -> str:
#         """
#         Retorna o idioma configurado para uma guild de forma síncrona.
#         Caso o idioma não esteja no cache, retorna o idioma padrão 'en'.

#         Parâmetros:
#             guild_id (Optional[str]): ID da guild para a qual o idioma será obtido.

#         Retorno:
#             str: Idioma configurado para a guild ou o padrão 'en'.
#         """
#         if guild_id and guild_id in self.language_cache:
#             guild_id = str(guild_id)
#             return self.language_cache[guild_id]
#         return "en"

#     def update_language_cache(self, guild_id: str, language: str):
#         """
#         Atualiza o cache local com o novo idioma da guild.
#         """
#         guild_id = str(guild_id)
#         self.language_cache[guild_id] = language

#     def load_global_translations(self, language: str) -> Dict[str, Any]:
#         """
#         Carrega e armazena traduções globais em cache para um idioma específico.
#         """
#         if language not in self.global_translations_cache:
#             path = Path(f"{self.global_path}/{language}.json")
#             if path.exists():
#                 with open(path, "r", encoding="utf-8") as f:
#                     self.global_translations_cache[language] = json.load(f)
#             else:
#                 self.global_translations_cache[language] = {}
#         return self.global_translations_cache[language]
    
#     def refresh_translation_cache(self):
#         """
#         Refresh the translation cache
#         """
#         modules = self.bot.modules
        
#         for module in modules:
#             translations_folder = Path(module.path) / module.data["translationsFolder"]
#             for language in translations_folder.rglob("*.json"):
                
#                 path = translations_folder / f"{language}.json"
#                 translations = {}
#                 if path.exists():
#                     with open(path, "r", encoding="utf-8") as f:
#                         translations = json.load(f)

#     def _get_nested_key(self, dictionary: Dict[str, Any], key: str) -> Any:
#         """
#         Busca uma chave aninhada em um dicionário usando "." como separador.
#         """
#         keys = key.split(".")
#         value = dictionary
#         for k in keys:
#             if isinstance(value, dict) and k in value:
#                 value = value[k]
#             else:
#                 return key  # Retorna a própria chave se não encontrada
#         return value

#     def get_global(self, language: str) -> Callable[[str, Any], str]:
#         """
#         Retorna uma função que pode ser usada para traduzir mensagens globais.
#         """
#         translations = self.load_global_translations(language)

#         def translate_global(key: str, **kwargs):
#             value = self._get_nested_key(translations, key)
#             if isinstance(value, str):
#                 value = self.bot.emoji_manager.replace_emojis(value) 
#                 return value.format(**kwargs)
#             return key  

#         return translate_global

#     def get_module_translations(self, module_name: str, language: str) -> Callable[[str, Any], str]:
#         cache_key = f"{module_name}:{language}"
#         if cache_key in self.module_translation_cache:
#             return self.module_translation_cache[cache_key]

#         # Carregar traduções como no método atual
#         module = self.bot.modules.get(module_name)
#         if not module:
#             self.logger.error(f"Module '{module_name}' not found.")
#             return lambda key, **kwargs: key

#         translations_folder = Path(module.path) / module.data["translationsFolder"]
#         path = translations_folder / f"{language}.json"
#         translations = {}
#         if path.exists():
#             with open(path, "r", encoding="utf-8") as f:
#                 translations = json.load(f)

#         def translate_module(key: str, **kwargs):
#             value = self._get_nested_key(translations, key)
#             if isinstance(value, str):
#                 value = self.bot.emoji_manager.replace_emojis(value, module_name) 
#                 return value.format(**kwargs)
#             return key

#         self.module_translation_cache[cache_key] = translate_module
#         return translate_module
    


#     def get_translation(self, key: str, language: str, module_name: Optional[str] = None) -> str:
#         """
#         Obtém a tradução processada para a chave especificada.

#         Args:
#             key (str): Chave da tradução.
#             language (str): Idioma.
#             module_name (Optional[str]): Nome do módulo.

#         Returns:
#             str: Tradução processada.
#         """
#         if module_name:
#             cache_key = f"{module_name}:{language}"
#             translations = self.module_translation_cache.get(cache_key, {})
#         else:
#             translations = self.global_translations_cache.get(language, {})

#         return self._get_nested_key(translations, key)
    
import json
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import logging



class Translator:
    def __init__(self, bot: ExtendedClient, global_path: str, logger: logging.Logger):
        self.bot = bot
        self.logger = logger
        self.global_path = Path(global_path)
        self.global_translations_cache = {}
        self.module_translation_cache = {}
        self.language_cache = {}

    async def get_language(self, guild_id: str) -> str:
        """
        Retorna o idioma configurado para uma guild. Padrão: 'en'.
        Atualiza o cache local quando necessário.
        """
        guild_id = str(guild_id)
        if guild_id in self.language_cache:
            return self.language_cache[guild_id]

        guild = await self.bot.guild_manager.fetch_or_create(guild_id)
        language = guild.data.get("language", "en")

        if language in ["Inglês", "English", "en", "en-US"]:
            self.language_cache[guild_id] = "en"
            language = "en"
        elif language in ["Português", "pt-br", "Português (Brasileiro)", "pt"]:
            self.language_cache[guild_id] = "pt"
            language = "pt"
        else:
            self.language_cache[guild_id] = language
        return language

    def get_language_sync(self, guild_id: Optional[str]) -> str:
        """
        Retorna o idioma configurado para uma guild de forma síncrona.
        Caso o idioma não esteja no cache, retorna o idioma padrão 'en'.

        Args:
            guild_id (Optional[str]): ID da guild para a qual o idioma será obtido.

        Returns:
            str: Idioma configurado para a guild ou o padrão 'en'.
        """
        if guild_id and guild_id in self.language_cache:
            guild_id = str(guild_id)
            return self.language_cache[guild_id]
        return "en"

    def update_language_cache(self, guild_id: str, language: str):
        """
        Atualiza o cache local com o novo idioma da guild.
        """
        guild_id = str(guild_id)
        self.language_cache[guild_id] = language

    def _process_emojis(self, text: str, module_name: Optional[str] = None) -> str:
        """
        Substitui placeholders de emojis no texto.

        Args:
            text (str): Texto com placeholders de emojis.
            module_name (Optional[str]): Nome do módulo.

        Returns:
            str: Texto com emojis processados.
        """
        if hasattr(self.bot, "emoji_manager"):
            return self.bot.emoji_manager.replace_emojis(text, module_name)
        return text

    def _process_translation(self, translations: Dict[str, Any], module_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Processa as traduções para incluir emojis.

        Args:
            translations (Dict[str, Any]): Traduções originais.
            module_name (Optional[str]): Nome do módulo.

        Returns:
            Dict[str, Any]: Traduções processadas.
        """
        processed = {}
        for key, value in translations.items():
            if isinstance(value, str):
                processed[key] = self._process_emojis(value, module_name)
            elif isinstance(value, dict):
                processed[key] = self._process_translation(value, module_name)
            else:
                processed[key] = value
        return processed

    async def refresh_translation_cache(self):
        """
        Atualiza o cache de traduções globais e de módulos de maneira assíncrona.
        """
        # Carregar traduções globais
        available_languages = {file.stem for file in self.global_path.glob("*.json")}
        for language in available_languages:
            path = self.global_path / f"{language}.json"
            if path.exists():
                try:
                    async with aiofiles.open(path, "r", encoding="utf-8") as f:
                        content = await f.read()
                        translations = json.loads(content)
                        self.global_translations_cache[language] = self._process_translation(translations)
                        self.logger.info(f"Global translations loaded for language: {language}")
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error loading global translations for {language}: {e}")

        # Carregar traduções dos módulos
        for module_name, module in self.bot.modules.items():
            translations_path = Path(module.path) / module.data.get("translationsFolder", "translations")
            available_languages = {file.stem for file in translations_path.glob("*.json")}
            for language in available_languages:
                path = translations_path / f"{language}.json"
                if path.exists():
                    try:
                        async with aiofiles.open(path, "r", encoding="utf-8") as f:
                            content = await f.read()
                            translations = json.loads(content)
                            processed_translations = self._process_translation(translations, module_name)
                            cache_key = f"{module_name}:{language}"
                            self.module_translation_cache[cache_key] = processed_translations
                            self.logger.info(f"Module translations loaded for {module_name}, language: {language}")
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Error loading module translations for {module_name}, language: {language}: {e}")

    def get_translation(self, key: str, language: str, module_name: Optional[str] = None) -> str:
        """
        Obtém a tradução processada para a chave especificada.

        Args:
            key (str): Chave da tradução.
            language (str): Idioma.
            module_name (Optional[str]): Nome do módulo.

        Returns:
            str: Tradução processada.
        """
        translations = (
            self.module_translation_cache.get(f"{module_name}:{language}", {})
            if module_name
            else self.global_translations_cache.get(language, {})
        )

        keys = key.split(".")
        for k in keys:
            if isinstance(translations, dict):
                translations = translations.get(k)
            else:
                return key  # Retorna a própria chave se não encontrada
        return translations if isinstance(translations, str) else key
    

    async def get_translator(self, guild_id: str, module_name: Optional[str] = None) -> Callable[[str], str]:
        """
        Retorna uma função assíncrona para obter traduções de forma reutilizável.

        Args:
            guild_id (str): ID da guild para determinar o idioma.
            module_name (Optional[str]): Nome do módulo, se aplicável.

        Returns:
            Callable[[str], str]: Função que aceita uma chave e retorna a tradução.
        """
        guild_id = str(guild_id)
        language = await self.get_language(guild_id=guild_id)

        def translator_func(key: str, **kwargs) -> str:
            value = self.get_translation(key=key, language=language, module_name=module_name)
            return value.format(**kwargs)

        return translator_func

    def get_translator_sync(self, language: str, module_name: Optional[str] = None) -> Callable[[str], str]:
        """
        Retorna uma função síncrona para obter traduções de forma reutilizável.

        Args:
            language (str): Idioma para traduções.
            module_name (Optional[str]): Nome do módulo, se aplicável.

        Returns:
            Callable[[str], str]: Função que aceita uma chave e retorna a tradução.
        """
        def translator_func(key: str, **kwargs) -> str:
            value = self.get_translation(key=key, language=language, module_name=module_name)
            return value.format(**kwargs)
        return translator_func
