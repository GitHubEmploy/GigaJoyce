from discord import app_commands, Interaction
from typing import Callable, Optional, Dict, Any


class DynamicCommand:
    """
    Represents a custom command that can be dynamically added to the command tree.
    """
    def __init__(
        self,
        name: str,
        description: str,
        callback: Callable[[Interaction], Any],
        parent: Optional[str] = None,  # ID of the parent command
    ):
        self.name = name
        self.description = description
        self.callback = callback
        self.parent = parent  # Parent command ID (if any)
        self.command = app_commands.Command(
            name=name,
            description=description,
            callback=callback,
        )


class DynamicRegistry:
    """
    Global registry for managing dynamic commands.
    """
    commands: Dict[str, DynamicCommand] = {}

    @classmethod
    def register(cls, command: DynamicCommand):
        """
        Register a custom command.
        """
        cls.commands[command.name] = command

        print(f"Registered command: {command.name} with parent: {command.parent}")

    @classmethod
    def get_commands(cls) -> Dict[str, DynamicCommand]:
        """
        Get all registered commands.
        """
        return cls.commands
