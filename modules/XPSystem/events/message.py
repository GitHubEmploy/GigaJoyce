from discord import Message
from discord.ext import commands
from ..manager.XPManager import XPManager

async def handle_xp_message(message: Message):
    """
    Event that increments a user's XP whenever they send a message.
    """
    if message.author.bot:
        return  # Ignore messages from bots to prevent loops and spam

    guild = message.guild
    if guild is None:
        return  # Ignore DMs

    guild_id = str(guild.id)
    user_id = str(message.author.id)
    client = message.channel.guild._state._get_client()
    
    xp_manager = XPManager()

    # Define the amount of XP to increment per message
    increment = 10  # Example: 10 XP per message

    # Update global XP
    # await xp_manager.update_global_xp(client, user_id, increment)

    # # Update local XP within the guild
    # await xp_manager.update_local_xp(client, guild_id, user_id, increment)

    # Optional: Provide feedback to the user (commented to avoid spam)
    # await message.channel.send(f"{message.author.mention}, you gained {increment} XP!")

# Exported events list
exports = [
    {
        "event": "on_message",
        "func": handle_xp_message
    }
]
