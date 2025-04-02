# # defaults/commands/settings.py

# import discord
# from discord import app_commands
# from typing import List, Any
# from fuzzywuzzy import process

# from classes.structs.SlashGroup import SlashGroup  # Your custom SlashGroup
# from settings.setting import default_save_method, Setting

# # --------------------------------------------------------------------
# # UTIL / PLACEHOLDER METHODS
# # --------------------------------------------------------------------
# def get_user_profile(interaction: discord.Interaction):
#     """
#     Retrieve the user's profile (placeholder function).
#     """
#     return interaction.client.user_profiles.get(interaction.user.id)

# async def settings_autocomplete(
#     interaction: discord.Interaction,
#     current: str
# ) -> List[app_commands.Choice[str]]:
#     """
#     Autocomplete for the 'setting_name' argument.
#     """
#     if not interaction.guild:
#         return []

#     guild = interaction.guild
#     profile = get_user_profile(interaction)

#     def test_condition(setting: Setting):
#         return setting.condition(guild, profile) if setting.condition else True

#     guild_settings = [
#         {"name": f"[Server] {s.name}", "setting": s}
#         for s in guild.settings if test_condition(s)
#     ]
#     user_settings = [
#         {"name": f"[User] {s.name}", "setting": s}
#         for s in profile.settings if test_condition(s)
#     ]
#     all_settings = guild_settings + user_settings

#     # Use fuzzy search
#     matches = process.extract(current, [s["setting"].name for s in all_settings], limit=25)
#     matched_names = dict(matches).keys()

#     filtered_settings = [s for s in all_settings if s["setting"].name in matched_names]

#     return [
#         app_commands.Choice(name=entry["name"], value=entry["setting"].name)
#         for entry in filtered_settings
#     ]

# # --------------------------------------------------------------------
# # CORE LOGIC: The subcommand callback
# # --------------------------------------------------------------------
# async def settings_command(
#     interaction: discord.Interaction,
#     setting_name: str
# ):
#     """
#     Main command logic to display or modify server settings.
#     Uses a deeper check for the user's manage_guild permission.
#     """
#     if not interaction.guild:
#         await interaction.response.send_message(
#             "This command can only be used in servers.",
#             ephemeral=True
#         )
#         return

#     # DEEPER CHECK: require manage_guild permission
#     if not interaction.user.guild_permissions.manage_guild:
#         await interaction.response.send_message(
#             "You need 'Manage Guild' permission to use this command.",
#             ephemeral=True
#         )
#         return

#     guild = interaction.guild
#     profile = get_user_profile(interaction)

#     # Attempt to locate the relevant setting in the guild or user
#     guild_setting = next((s for s in guild.settings if s.name == setting_name), None)
#     user_setting = next((s for s in profile.settings if s.name == setting_name), None)

#     # Check for conflict
#     if guild_setting and user_setting:
#         await interaction.response.send_message(
#             "The setting exists in both guild and user settings. "
#             "This shouldn't happen. Please contact the developer.",
#             ephemeral=True
#         )
#         return

#     if not guild_setting and not user_setting:
#         await interaction.response.send_message("Setting not found.", ephemeral=True)
#         return

#     setting = guild_setting or user_setting

#     # Additional permission or condition checks
#     if setting.permission and not interaction.user.guild_permissions.has(setting.permission):
#         await interaction.response.send_message(
#             "You don't have permission to modify this setting.",
#             ephemeral=True
#         )
#         return

#     if setting.condition and not setting.condition(guild, profile):
#         await interaction.response.send_message(
#             "This setting is not currently available for you.",
#             ephemeral=True
#         )
#         return

#     # Execute setting logic
#     result = await setting.run(interaction)
#     setting.value = None if result is None else result

#     # If it's a guild setting, invalidate the cache
#     if guild_setting:
#         interaction.client.guild_handler.invalidate_cache(interaction.guild.id)

#     # Save the updated setting
#     if setting.save:
#         await setting.save(guild, result, profile)
#     else:
#         entity = guild if guild_setting else profile
#         await default_save_method(interaction.client, entity, setting)

#     await interaction.response.send_message(
#         f"Setting '{setting.name}' has been updated successfully.",
#         ephemeral=True
#     )

# # --------------------------------------------------------------------
# # 1) Create the underlying app_commands.Group
# # --------------------------------------------------------------------
# settings_app_group = app_commands.Group(
#     name="settings",
#     description="Show or modify server settings"
#     # No default_member_permissions, we do deeper checks in callback
# )

# # 2) Define the subcommand in the group
# @settings_app_group.command(
#     name="modify",
#     description="View or change a server/user setting",
# )
# @app_commands.describe(setting_name="Which setting do you want to change?")
# @app_commands.autocomplete(setting_name=settings_autocomplete)
# async def modify_subcommand(
#     interaction: discord.Interaction,
#     setting_name: str
# ):
#     """
#     Subcommand that calls settings_command logic for deeper checks.
#     """
#     await settings_command(interaction, setting_name)

# # --------------------------------------------------------------------
# # 3) Wrap it in SlashGroup
# # --------------------------------------------------------------------
# settings_group = SlashGroup(
#     group=settings_app_group,
#     global_cmd=True,
#     # We do not set default_permissions here
# )

# # --------------------------------------------------------------------
# # 4) Export for dynamic loading
# # --------------------------------------------------------------------
# default = [
#     settings_group
# ]
