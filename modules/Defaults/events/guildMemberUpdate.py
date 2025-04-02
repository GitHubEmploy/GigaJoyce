import discord

async def on_guild_member_update(before: discord.Member, after: discord.Member):
    """
    Handles updates to a member's roles or premium subscription status.
    """
    # Role added
    if len(before.roles) < len(after.roles):
        added_role = next(role for role in after.roles if role not in before.roles)
        if added_role:
            print(f"Role added: {added_role.name} to {after.display_name}")

    # Role removed
    if len(before.roles) > len(after.roles):
        removed_role = next(role for role in before.roles if role not in after.roles)
        if removed_role:
            print(f"Role removed: {removed_role.name} from {after.display_name}")

    # Check for premium subscriber role
    booster_role = after.guild.premium_subscriber_role
    if booster_role:
        if booster_role not in before.roles and booster_role in after.roles:
            print(f"New booster: {after.display_name}")

# Event dictionary for dynamic loading
event = {
    "event": "on_guild_member_update",
    "func": on_guild_member_update
}
