from discord.ext import commands
from discord import app_commands, Interaction


@commands.command(name="show_commands")
async def show_commands(ctx):
    """
    Mostra todos os comandos registrados na árvore de comandos.
    """
    commands = []
    for command in self.bot.tree.get_commands():
        if isinstance(command, app_commands.Group):
            subcommands = [subcmd.name for subcmd in command.commands]
            commands.append(f"{command.name} (Grupo): {', '.join(subcommands)}")
        else:
            commands.append(f"{command.name}")
    await ctx.send(f"**Comandos Registrados:**\n" + "\n".join(commands))

exports = [show_commands]
