# # defaults/commands/permissions.py

# import discord
# from discord import app_commands
# import yaml
# import aiohttp
# from typing import Any
# import io

# from classes.structs.SlashGroup import SlashGroup  # Your custom wrapper
# from handlers.commandHandler import Command, SlashCommand  # If needed
# # from classes.structs.Permissions import Permissions  # If you want advanced perms logic

# def try_parse_yaml(value: str) -> Any:
#     """
#     Parse YAML string to Python object. Returns None if parsing fails.
#     """
#     try:
#         return yaml.safe_load(value)
#     except yaml.YAMLError:
#         return None


# # 1) Create the underlying app_commands.Group
# permissions_app_group = app_commands.Group(
#     name="permissions",
#     description="Manage permission overrides",
# )


# # 2) Define a subcommand for setting permissions
# @permissions_app_group.command(
#     name="set",
#     description="Set permission overrides using a YAML file."
# )
# @app_commands.describe(permission="Attach a YAML file with 'overrides'")
# async def set_permissions(
#     interaction: discord.Interaction,
#     permission: discord.Attachment
# ):
#     """
#     Set permission overrides using a YAML attachment.
#     Deep check: requires the user to have administrator permission.
#     """
#     if not interaction.user.guild_permissions.administrator:
#         await interaction.response.send_message(
#             "You must have 'Administrator' permission to use this command.",
#             ephemeral=True
#         )
#         return

#     if not permission.content_type or "text/plain" not in permission.content_type:
#         await interaction.response.send_message(
#             "Invalid attachment. Please upload a valid YAML file.",
#             ephemeral=True
#         )
#         return

#     async with aiohttp.ClientSession() as session:
#         async with session.get(permission.url) as response:
#             if response.status != 200:
#                 await interaction.response.send_message(
#                     "Failed to download the attachment. Try again.",
#                     ephemeral=True
#                 )
#                 return
#             data = await response.text()

#     parsed_yaml = try_parse_yaml(data)
#     if not parsed_yaml or "overrides" not in parsed_yaml:
#         await interaction.response.send_message(
#             "Invalid YAML format. Ensure it contains 'overrides'.",
#             ephemeral=True
#         )
#         return

#     overrides = parsed_yaml["overrides"]
#     logs = []
#     permissions_map = {}

#     for override in overrides:
#         if "allow" not in override and "deny" not in override:
#             logs.append(f"Invalid permission base for {override.get('id', 'unknown')}")
#             continue

#         override_id = override.get("id")
#         if not override_id:
#             logs.append("Missing override ID in one of the entries.")
#             continue

#         allow = override.get("allow", [])
#         deny = override.get("deny", [])
#         permissions_map[override_id] = {"allow": allow, "deny": deny}

#     if logs:
#         await interaction.response.send_message("\n".join(logs), ephemeral=True)
#         return

#     # Save overrides to database
#     guild_data = await interaction.client.db.find_one("guilds", {"guild_id": interaction.guild.id})
#     if not guild_data:
#         guild_data = {"guild_id": interaction.guild.id, "permissions_overrides": {}}

#     guild_data["permissions_overrides"] = permissions_map
#     await interaction.client.db.update_one(
#         "guilds",
#         {"guild_id": interaction.guild.id},
#         {"$set": {"permissions_overrides": permissions_map}},
#         upsert=True
#     )

#     await interaction.response.send_message("Permissions updated successfully.", ephemeral=True)


# # 3) Define a subcommand to list permissions
# @permissions_app_group.command(
#     name="list",
#     description="List all permission overrides."
# )
# async def list_permissions(interaction: discord.Interaction):
#     """
#     List all permission overrides and export them as a YAML file.
#     Deep check: requires the user to have administrator permission.
#     """
#     if not interaction.user.guild_permissions.administrator:
#         await interaction.response.send_message(
#             "You must have 'Administrator' permission to use this command.",
#             ephemeral=True
#         )
#         return

#     guild_data = await interaction.client.db.find_one("guilds", {"guild_id": interaction.guild.id})
#     if not guild_data or "permissions_overrides" not in guild_data:
#         await interaction.response.send_message(
#             "No permission overrides found.",
#             ephemeral=True
#         )
#         return

#     permissions_overrides = guild_data["permissions_overrides"]
#     yaml_data = yaml.safe_dump({"overrides": permissions_overrides}, sort_keys=False)

#     file = discord.File(fp=io.BytesIO(yaml_data.encode("utf-8")), filename="overrides.yaml")
#     await interaction.response.send_message("Here are the permission overrides:", file=file)


# # 4) Wrap the group in a SlashGroup for your loader
# permissions_group = SlashGroup(
#     group=permissions_app_group,
#     global_cmd=True,
# )

# # 5) Export for dynamic loading
# default = [
#     permissions_group
# ]
