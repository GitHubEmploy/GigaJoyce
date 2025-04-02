from discord import Member, Message
from discord.ext import commands

prefix = 'j!'

def check_overrides_for_type(override: dict, user: Member, chan_id: str) -> bool:
    """
    Check if a user, role, or channel has specific overrides.
    """
    if user.id in override.get('users', []):
        return True
    if any(role.id in override.get('roles', []) for role in user.roles):
        return True
    if chan_id in override.get('channels', []):
        return True
    return False

async def on_message(bot: commands.Bot, message: Message):
    """
    Handles the `on_message` event dynamically via a dictionary.
    """
    
    
    if message.author.bot or not message.guild:
        return

    if message.content.startswith(prefix):
        args = message.content[len(prefix):].strip().split()
        command_name = args.pop(0).lower() if args else None

        if not command_name:
            return

        # Check native Discord commands first
        ctx = await bot.get_context(message)
        if ctx.command:
            await bot.invoke(ctx)
            return

        # Check custom commands
        print(f"Custom commands: {bot.custom_commands}")
        command = bot.custom_commands.get(command_name)
        if not command:
            await message.reply(f"The command `{command_name}` does not exist.")
            return
        print(f"Command called: {command}")
        try:
            profile = await bot.profile_handler.fetch_or_create(message.author.id, message.guild.id)

            # Execute the command
            await command(
                client=bot,
                message=message,
                args=args,
                profile=profile,
                logger=command.logger if hasattr(command, 'logger') else bot.logger,
                guild=ctx.guild,
                interfacer=None,
                used_name=command_name,
            )
        except Exception as e:
            print(f"Error executing command '{command_name}': {e}")
            await message.reply("An error occurred while executing the command.")



# Event dictionary
event = {
    "event": "on_message",
    "func": on_message
}
