import json
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from logging import Logger
from discord.ext import commands
from classes.structs.Module import Module
from shared.types import ExtendedClient
import sys


class ModuleHandler:
    """
    Responsible for discovering, initializing, and managing modules.
    """

    def __init__(self, bot: ExtendedClient, logger: Logger):
        self.bot = bot
        self.logger = logger
        self.modules_path = Path("./modules")
        self.loaded_modules: Dict[str, Module] = {}
        
    def register_permissions(self, module_name: str, permissions: List[str]):
        """
        Register permissions for a module.

        Args:
            module_name (str): The name of the module.
            permissions (List[str]): A list of permission strings to register.
        """
        for permission in permissions:
            try:
                self.bot.permission_manager.register_node(permission, lambda client, node, member, channel: True)
                self.logger.info(f"Permission '{permission}' registered for module '{module_name}'.")
            except Exception as e:
                self.logger.error(f"Failed to register permission '{permission}' for module '{module_name}': {e}")


    async def load_modules(self, specific_module: Optional[str] = None):
        """
        Dynamically load all modules from the specified path.
        """
        modules_path = self.modules_path

        for module_folder in modules_path.iterdir():
            if not module_folder.is_dir():
                continue
            
            if specific_module and module_folder.name != specific_module:
                continue

            manifest_path = module_folder / "manifest.json"
            if not manifest_path.exists():
                self.logger.warning(f"Manifest not found for module: {module_folder.name}")
                continue

            # Load the module's manifest
            try:
                with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                    manifest = json.load(manifest_file)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse manifest for module {module_folder.name}: {e}")
                continue

            # Extract module information
            name = manifest.get("name", module_folder.name)
            self.logger.info(f"Loading {name} module...")
            description = manifest.get("description", "No description provided.")
            version = manifest.get("version", "1.0.0")
            color = manifest.get("color", "#FFFFFF")
            setup_file = module_folder / manifest.get("initFile", "main.py")

            commands_folder = module_folder / manifest.get("commandsFolder", "commands")
            events_folder = module_folder / manifest.get("eventsFolder", "events")
            translations_folder = module_folder / manifest.get("translationsFolder", "translations")

            base_package = f"modules.{module_folder.name}.commands"

            # Execute the setup function and retrieve interface and settings
            setup_data = self._execute_setup(setup_file)
            if setup_data is None:
                self.logger.error(f"Setup failed for module {name}. Skipping module.")
                continue

            interface = setup_data.get("interface", {})
            settings = setup_data.get("settings", [])
            user_settings = setup_data.get("userSettings", [])

            # Create the module instance
            module = Module(
                name=name,
                path=str(module_folder),
                description=description,
                version=version,
                color=color,
                logger=self.logger,
                init_func=setup_data.get("initFunc"),
                data=manifest,
                commands={"text": {}, "slash": {}},
                interfacer=interface,
                settings=settings,
                user_settings=user_settings,
            )

            if self.bot.command_handler:
                await self.bot.command_handler.load_commands_from_folder(commands_folder, base_package, module)
            else:
                self.logger.error("CommandHandler is not initialized.")

            # Load events
            if self.bot.event_handler:
                self.bot.event_handler.load_events_from_module(name, events_folder, module)
            else:
                self.logger.error("EventHandler is not initialized.")

            # Store the module in the loaded modules dictionary
            self.loaded_modules[name] = module
            self.logger.info(f"Successfully loaded module: {name}")

        self.bot.modules = self.loaded_modules

    def _execute_setup(self, setup_file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Executes the setup function from the module's init file.

        Args:
            setup_file_path (Path): Path to the init file.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing 'interface', 'settings', and 'managers' if successful.
        """
        if not setup_file_path.exists():
            self.logger.warning(f"Init file not found: {setup_file_path}")
            return None

        module_name = f"init_{setup_file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, setup_file_path)
        if spec is None:
            self.logger.error(f"Failed to load init file: {setup_file_path}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        loader = spec.loader
        if loader is None:
            self.logger.error(f"Loader not found for init file: {setup_file_path}")
            return None

        try:
            loader.exec_module(module)
            setup_func = getattr(module, "setup", None)
            if callable(setup_func):
                setup_data = setup_func(self.bot, self.logger)
                if isinstance(setup_data, dict):
                    return setup_data
                else:
                    self.logger.error(f"Setup function in {setup_file_path} did not return a dictionary.")
                    return None
            else:
                self.logger.error(f"No callable 'setup' function found in {setup_file_path}.")
                return None
        except Exception as e:
            self.logger.error(f"Error executing setup function in {setup_file_path}: {e}")
            return None

    async def unload_modules(self):
        """
        Unloads all modules dynamically.
        """
        for module_name, module in list(self.loaded_modules.items()):
            try:
                await module.unload(self.bot)
                del self.loaded_modules[module_name]
                self.logger.info(f"Unloaded module: {module_name}")
            except Exception as e:
                self.logger.error(f"Failed to unload module {module_name}: {e}")

    async def reload_modules(self):
        """
        Reloads all modules dynamically.
        """
        await self.unload_modules()
        await self.load_modules()