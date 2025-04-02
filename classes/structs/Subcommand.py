from discord import app_commands, Interaction
from typing import Callable

class Subcommand:
    """
    Classe para definir subcomandos dinâmicos.
    """

    def __init__(self, name: str, description: str, callback: Callable, parent_name: str = None):
        self.name = name
        self.description = description
        self.callback = callback
        self.parent_name = parent_name

    def to_app_command(self) -> app_commands.Command:
        """
        Converte a instância em um app command.
        """
        return app_commands.Command(
            name=self.name,
            description=self.description,
            callback=self.callback,
        )
