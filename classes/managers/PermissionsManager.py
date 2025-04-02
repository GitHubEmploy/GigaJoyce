# classes/managers/PermissionsManager.py

from typing import Dict, Optional, Any, Union
from discord.ext.commands import Bot
from discord import TextChannel
from discord import Member as GuildMember
from shared.types import PermissionNode, RecursiveMap, OverrideNode
import logging


def is_end_node(node: Union[PermissionNode, RecursiveMap]) -> bool:
    """
    Checks if the node is an end node.
    """
    return not isinstance(node, dict)

class PermissionsManager:
    def __init__(self, client: Bot, logger: logging.Logger):
        self.client = client
        self.logger = logger
        self.permissions: RecursiveMap = {}

    def register_node(self, permission: str, result: PermissionNode):
        namespaces = permission.split('.')
        current = self.permissions
        last = namespaces.pop() if namespaces else None

        if not last:
            self.logger.warning("No namespaces provided for permission registration.")
            return

        for namespace in namespaces:
            if namespace not in current:
                current[namespace] = {}
            elif not isinstance(current[namespace], dict):
                self.logger.error(f"Cannot create namespace '{namespace}' as it's already an end node.")
                return
            current = current[namespace]

        current[last] = result

    def get_node(self, permission: str) -> Optional[PermissionNode]:
        namespaces = permission.split('.')
        current = self.permissions
        last_global: Optional[PermissionNode] = None

        for namespace in namespaces:
            if namespace in current:
                node = current[namespace]
                if is_end_node(node):
                    return node
                current = node
            elif '*' in current:
                last_global = current['*']
            else:
                return last_global

        return current if is_end_node(current) else last_global

    async def check_permission_for(self, node: str, member: GuildMember, channel: TextChannel) -> bool:
        permission_node = self.get_node(node)
        if not permission_node:
            self.logger.warning(f"Permission node '{node}' not found.")
            return False

        try:
            result = await permission_node(self.client, node, member, channel)
            return result
        except Exception as e:
            self.logger.error(f"Error executing permission node '{node}': {e}")
            return False

    async def compute_permissions(self, override: OverrideNode, member: GuildMember, channel: TextChannel) -> Optional[bool]:
        for allow_perm in override.get('allow', []):
            if await self.check_permission_for(allow_perm, member, channel):
                return True

        for deny_perm in override.get('deny', []):
            if await self.check_permission_for(deny_perm, member, channel):
                return False

        return None

    async def has_permission(self, node: str, member: GuildMember, channel: TextChannel, override: OverrideNode) -> bool:
        discord_permission = getattr(member.guild_permissions, node.split('.')[-1], False)
        if discord_permission:
            return True

        override_result = await self.compute_permissions(override, member, channel)
        if override_result is not None:
            return override_result

        return False
