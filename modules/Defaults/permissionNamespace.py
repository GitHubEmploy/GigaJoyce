from typing import Optional
from discord import Member as GuildMember, TextChannel
from shared.types import ExtendedClient

def RolesNamespace(client: ExtendedClient, node: str, member: GuildMember, channel: Optional[TextChannel]) -> bool:
    """
    Check if a GuildMember has a specific role based on the node.

    Args:
        client (ExtendedClient): The bot client.
        node (str): The hierarchical permission node (e.g., "Role.<role_id>").
        member (GuildMember): The member to check.
        channel (Optional[TextChannel]): The channel where the permission is being checked.

    Returns:
        bool: True if the member has the specified role, False otherwise.
    """
    broken = node.split(".")
    role_id = broken.pop()
    if not role_id:
        return False
    return any(role.id == int(role_id) for role in member.roles)

def ChannelsNamespace(client: ExtendedClient, node: str, member: GuildMember, channel: Optional[TextChannel]) -> bool:
    """
    Check if a TextChannel matches the specific node.

    Args:
        client (ExtendedClient): The bot client.
        node (str): The hierarchical permission node (e.g., "Channel.<channel_id>").
        member (GuildMember): The member to check (not used here).
        channel (Optional[TextChannel]): The channel where the permission is being checked.

    Returns:
        bool: True if the channel matches the specified channel_id, False otherwise.
    """
    broken = node.split(".")
    channel_id = broken.pop()
    if not channel_id or not channel:
        return False
    return channel.id == int(channel_id)

def UsersNamespace(client: ExtendedClient, node: str, member: GuildMember, channel: Optional[TextChannel]) -> bool:
    """
    Check if a GuildMember matches a specific user ID in the node.

    Args:
        client (ExtendedClient): The bot client.
        node (str): The hierarchical permission node (e.g., "User.<user_id>").
        member (GuildMember): The member to check.
        channel (Optional[TextChannel]): The channel where the permission is being checked (not used here).

    Returns:
        bool: True if the member's ID matches the specified user_id, False otherwise.
    """
    broken = node.split(".")
    user_id = broken.pop()
    if not user_id:
        return False
    return member.id == int(user_id)
