from typing import Callable, List, Optional
import logging
from discord.ext import commands

class Command:
    """
    Represents a text-based command that integrates with discord.ext.commands.
    Designed to be used as a decorator.
    """

    def __init__(
        self,
        name: str,
        description: str,
        how_to_use: str,
        aliases: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.name = name
        self.description = description
        self.how_to_use = how_to_use
        self.aliases = aliases or []
        self.logger = logger or logging.getLogger(name)
        self.func: Optional[Callable] = None  # Placeholder for the decorated function

    def __call__(self, func: Callable) -> "Command":
        """
        Decorator to attach a function to the command.
        """
        self.func = func  # Capture the decorated function
        return self

    def get_command_function(self) -> Callable:
        """
        Returns the original command function.
        """
        if not self.func:
            raise RuntimeError(f"Command '{self.name}' has no associated function.")
        return self.func

    def register(self, bot: commands.Bot):
        """
        Register this command with the bot's command registry.
        """
        async def wrapped(ctx, *args, **kwargs):
            await self.func(
                client=bot,
                message=ctx.message,
                args=args,
                profile=None,  # Adjust as needed to fetch user profile
                logger=self.logger,
                guild=ctx.guild,
                interfacer=None,
                used_name=self.name,
            )

        bot.command(
            name=self.name,
            description=self.description,
            aliases=self.aliases,
        )(wrapped)

        print(f"Registered command '{self.name}' with the bot.")
