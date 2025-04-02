import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path
import yaml
import aiohttp
import io
from typing import Any, Dict, List, Union
from classes.structs.Permissions import Permissions
from shared.types import OverrideNode, PermissionOverrideTree, ExtendedClient

class PermissionsCommand(commands.Cog):
    def __init__(self, bot: ExtendedClient):
        self.bot = bot

    async def try_parse_yaml(self, value: str) -> Any:
        try:
            return yaml.safe_load(value)
        except yaml.YAMLError:
            return None

    @staticmethod
    def is_end_node(node: Union[OverrideNode, PermissionOverrideTree]) -> bool:
        return not isinstance(node, dict)

    # Criação de um grupo de comandos
    permissions_group = app_commands.Group(name="permissions", description="Grupo de permissões")

    @permissions_group.command(name="set", description="Definir permissões a partir de um arquivo YAML")
    @app_commands.default_permissions(administrator=True)
    async def permissions_set(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id if interaction.guild else None
        translate = await self.bot.translator.get_translator(guild_id=guild_id, module_name="Defaults")

        attachment = interaction.data.get("attachments", [])[0] if interaction.data.get("attachments") else None
        if not attachment or "text/plain" not in attachment.content_type:
            await interaction.response.send_message(translate("permissions.invalid_attachment"), ephemeral=True)
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await interaction.response.send_message(translate("permissions.invalid_attachment"), ephemeral=True)
                    return
                data = await resp.text()

        parsed_data = await self.try_parse_yaml(data)
        if not parsed_data or not isinstance(parsed_data.get("overrides"), list):
            await interaction.response.send_message(translate("permissions.invalid_permission_data"), ephemeral=True)
            return

        logs = []
        translated_overrides = Permissions(self.bot.logger, {})

        for override in parsed_data["overrides"]:
            allow = override.get("permitir", [])
            deny = override.get("negar", [])
            if not allow and not deny:
                logs.append(translate("permissions.invalid_base_permission").format(id=override.get("id")))
                continue

            for module in deny:
                node = translated_overrides.get_end_node(module, strict=True)
                if not node:
                    translated_overrides.set(module, {"allow": [], "deny": [override["id"]]})
                else:
                    node["deny"].append(override["id"])
                    translated_overrides.set(module, node)

            for module in allow:
                node = translated_overrides.get_end_node(module, strict=True)
                if not node:
                    translated_overrides.set(module, {"allow": [override["id"]], "deny": []})
                else:
                    node["allow"].append(override["id"])
                    translated_overrides.set(module, node)

        if logs:
            await interaction.response.send_message("\n".join(logs), ephemeral=True)
            return

        guild = await self.bot.guild_manager.fetch_or_create(interaction.guild_id)
        guild_data = guild.data
        guild_data["permissionsOverrides"] = translated_overrides.permissions
        await guild_data.save()

        await interaction.response.send_message(translate("permissions.updated_successfully"), ephemeral=True)

    @permissions_group.command(name="list", description="Listar as permissões configuradas")
    @app_commands.default_permissions(administrator=True)
    async def permissions_list(self, interaction: discord.Interaction):

        guild_id = interaction.guild.id if interaction.guild else None
        translate = await self.bot.translator.get_translator(guild_id=guild_id, module_name="Defaults")
        
        guild = await self.bot.guild_manager.fetch_or_create(interaction.guild_id)
        
        permissions_tree = guild.data.get("permissionsOverrides", {})

        translated_overrides = {"overrides": []}

        def recurse_through_tree(permissions, path=""):
            for branch, value in permissions.items():
                full_path = f"{path}.{branch}" if path else branch
                if self.is_end_node(value):
                    for allow in value.get("allow", []):
                        existing = next((o for o in translated_overrides["overrides"] if o["id"] == allow), None)
                        if not existing:
                            translated_overrides["overrides"].append({"id": allow, "permitir": [full_path], "negar": []})
                        elif full_path not in existing["permitir"]:
                            existing["permitir"].append(full_path)

                    for deny in value.get("deny", []):
                        existing = next((o for o in translated_overrides["overrides"] if o["id"] == deny), None)
                        if not existing:
                            translated_overrides["overrides"].append({"id": deny, "permitir": [], "negar": [full_path]})
                        elif full_path not in existing["negar"]:
                            existing["negar"].append(full_path)
                else:
                    recurse_through_tree(value, full_path)

        recurse_through_tree(permissions_tree)

        yaml_output = yaml.dump(translated_overrides, allow_unicode=True)
        buffer = io.BytesIO(yaml_output.encode('utf-8'))
        file = discord.File(fp=buffer, filename="overrides.yaml")

        await interaction.response.send_message(translate("permissions.list_success"), file=file, ephemeral=True)

exports = [PermissionsCommand]
