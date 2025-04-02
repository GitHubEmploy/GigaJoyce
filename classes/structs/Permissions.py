from typing import Dict, Union, Optional
from shared.types import OverrideNode, PermissionOverrideTree
import logging

from typing import Dict, Union, Optional
from shared.types import OverrideNode, PermissionOverrideTree
import logging


def is_end_node(node: Union[OverrideNode, PermissionOverrideTree]) -> bool:
    """Checks if a node in the permissions tree is an end node."""
    return not isinstance(node, dict)


class Permissions:
    def __init__(self, logger: logging.Logger, permissions: PermissionOverrideTree):
        self.logger = logger
        self.permissions = permissions

    def set(self, permission: str, result: OverrideNode):
        namespaces = permission.split(".")
        current = self.permissions
        last = namespaces.pop()

        if not last:
            self.logger.warning("No namespaces provided.")
            return

        for namespace in namespaces:
            if namespace not in current:
                current[namespace] = {}
            elif is_end_node(current[namespace]):
                self.logger.error(f"Cannot create namespace '{namespace}' as it's already an end node.")
                return
            current = current[namespace]

        current[last] = result

    def get(self, permission: str, strict: bool = False) -> Optional[Union[OverrideNode, PermissionOverrideTree]]:
        namespaces = permission.split(".")
        current = self.permissions
        last_global: Optional[OverrideNode] = None

        for namespace in namespaces:
            if namespace in current:
                node = current[namespace]
                if is_end_node(node):
                    return node
                current = node
            elif '*' in current:
                last_global = current['*']
            else:
                return last_global if not strict else None

        return current if is_end_node(current) else last_global

    def get_end_node(self, permission: str, strict: bool = False) -> Optional[OverrideNode]:
        node = self.get(permission, strict)
        return node if is_end_node(node) else None

    def get_or_create_path(self, permission: str) -> PermissionOverrideTree:
        namespaces = permission.split(".")
        current = self.permissions

        for namespace in namespaces:
            if namespace not in current:
                current[namespace] = {}
            current = current[namespace]

        return current
