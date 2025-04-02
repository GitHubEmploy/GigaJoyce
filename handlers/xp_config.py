# # modules/XPSystem/commands/xp_config.py

# from discord.ext.commands import MemberConverter, Bot
# from classes.structs.Command import Command
# from classes.structs.Guild import Guild
# from typing import Any, Optional
# import discord

# @Command(
#     name="set_xp_multiplier",
#     description="Set XP multiplier for a specific role.",
#     how_to_use="set_xp_multiplier <roleName> <multiplier>",
#     aliases=[]
# )
# async def set_xp_multiplier_text(
#     client: Bot,
#     message: discord.Message,
#     args: list,
#     profile: Any,
#     logger: Any,
#     guild: Guild,
#     interfacer: Any = None,
#     used_name: Optional[str] = None,
# ):
#     """
#     Set XP multiplier for a specific role.
#     """
#     if not message.author.guild_permissions.manage_guild:
#         await message.reply("You need 'Manage Server' permission.")
#         return

#     if len(args) < 2:
#         await message.reply("Usage: `set_xp_multiplier <roleName> <multiplier>`")
#         return

#     role_name = args[0]
#     try:
#         multiplier = float(args[1])
#     except ValueError:
#         await message.reply("Multiplier must be a number.")
#         return

#     if multiplier < 1.0:
#         await message.reply("Multiplier must be at least 1.0.")
#         return

#     try:
#         current_multipliers = guild.data.get("settings", {}).get("role_xp_multipliers", {})
#         current_multipliers[role_name] = multiplier
#         await guild.update_setting("role_xp_multipliers", current_multipliers)
#         await message.reply(f"Set XP multiplier for role **{role_name}** to **{multiplier}**.")
#         logger.debug(f"Set XP multiplier for role {role_name} to {multiplier} in guild {guild.id}")
#     except Exception as e:
#         logger.error(f"Error setting XP multiplier: {e}")
#         await message.reply("An error occurred while setting the XP multiplier.")


# @Command(
#     name="set_role_stack",
#     description="Set whether roles stack or replace each other.",
#     how_to_use="set_role_stack <true/false>",
#     aliases=[]
# )
# async def set_role_stack_text(
#     client: Bot,
#     message: discord.Message,
#     args: list,
#     profile: Any,
#     logger: Any,
#     guild: Guild,
#     interfacer: Any = None,
#     used_name: Optional[str] = None,
# ):
#     """
#     Set whether roles stack or replace each other.
#     """
#     if not message.author.guild_permissions.manage_guild:
#         await message.reply("You need 'Manage Server' permission.")
#         return

#     if len(args) < 1:
#         await message.reply("Usage: `set_role_stack <true/false>`")
#         return

#     stack_input = args[0].lower()
#     if stack_input not in ("true", "false"):
#         await message.reply("Please use `true` or `false`.")
#         return

#     stack_roles = (stack_input == "true")
#     try:
#         await guild.update_setting("stack_roles", stack_roles)
#         await message.reply(f"Role stacking is **{'enabled' if stack_roles else 'disabled'}**.")
#         logger.debug(f"Set role stacking to {stack_roles} in guild {guild.id}")
#     except Exception as e:
#         logger.error(f"Error setting role stacking: {e}")
#         await message.reply("An error occurred while setting role stacking.")


# @Command(
#     name="get_xp_config",
#     description="Get the guild's XP configuration.",
#     how_to_use="get_xp_config",
#     aliases=[]
# )
# async def get_xp_config_text(
#     client: Bot,
#     message: discord.Message,
#     args: list,
#     profile: Any,
#     logger: Any,
#     guild: Guild,
#     interfacer: Any = None,
#     used_name: Optional[str] = None,
# ):
#     """
#     Get the guild's XP configuration.
#     """
#     if not message.author.guild_permissions.manage_guild:
#         await message.reply("You need 'Manage Server' permission.")
#         return

#     try:
#         config = guild.data.get("settings", {})
#         role_multipliers = config.get("role_xp_multipliers", {})
#         stack_roles = config.get("stack_roles", False)

#         if not role_multipliers:
#             multiplier_list = "None"
#         else:
#             multiplier_list = "\n".join(f"• **{role}**: {mult}" for role, mult in role_multipliers.items())

#         await message.reply(
#             f"**Guild XP Configuration (Text):**\n"
#             f"**Role Multipliers:**\n{multiplier_list}\n"
#             f"**Role Stacking:** {'Enabled' if stack_roles else 'Disabled'}"
#         )
#         logger.debug(f"Retrieved XP configuration for guild {guild.id}")
#     except Exception as e:
#         logger.error(f"Error retrieving XP configuration: {e}")
#         await message.reply("An error occurred while retrieving the XP configuration.")


# # Expose the commands for the loader
# default = [
#     set_xp_multiplier_text,
#     set_role_stack_text,
#     get_xp_config_text,
# ]

# print("Default commands:", default)
