# modules/XPSystem/commands/xp.py

from discord import app_commands, Interaction
from classes.structs.CommandHelp import CommandHelp
from utils.Loader import load_translation  # Utility function to load translations
from discord.ext.commands import Bot
from classes.managers.SettingsManager import SettingsManager  # Ensure correct import path

# Callback for the main XP command
@app_commands.command(name="xp", description="Show XP and level for a member.")
async def xp(interaction: Interaction):
    """
    Main XP command to display a user's XP and level.
    """
    guild_id = interaction.guild_id
    user_id = interaction.user.id

    # Ensure the command is used within a guild
    if guild_id is None:
        await interaction.response.send_message("This command can only be used within a server.", ephemeral=True)
        return

    # Retrieve the language setting for the guild
    settings_handler: SettingsManager = interaction.client.settings_handler
    guild_language = settings_handler.get_language(guild_id)

    # Load translated messages
    try:
        translations = load_translation("XPSystem", "xp", guild_language)
    except (FileNotFoundError, ValueError) as e:
        await interaction.response.send_message("An error occurred while loading translations.", ephemeral=True)
        interaction.client.get_logger("TranslationLoader").error(f"Translation error: {e}")
        return

    # Access the XPManager from the XPSystem module
    xp_system_module = interaction.client.modules.get("XPSystem")
    if not xp_system_module or not hasattr(xp_system_module, "xp_manager"):
        await interaction.response.send_message("XP system is not available.", ephemeral=True)
        interaction.client.get_logger("XPSystem").error("XPManager not found in XPSystem module.")
        return

    xp_manager = xp_system_module.xp_manager

    # Retrieve XP data
    user_xp = await xp_manager.get_user_xp(str(guild_id), str(user_id))

    global_xp = user_xp["global_xp"]["total_xp"]
    global_level = user_xp["global_xp"]["level"]

    local_xp = user_xp["local_xp"]["xp"]
    local_level = user_xp["local_xp"]["level"]

    # Prepare the message using translations and dynamic data
    message = translations.get(
        "xp_current_xp",
        "You currently have {xp} XP and are at level {level}."
    ).format(
        xp=local_xp,
        level=local_level
    )

    await interaction.response.send_message(message, ephemeral=True)


# Detailed help for the XP command
xp_detailed_help = CommandHelp(
    name="xp",
    translations={
        "en": {
            "description": "Shows the current XP and level of a user.",
            "usage": "/xp [user]",
            "examples": ["/xp", "/xp @User123"]
        },
        "pt": {
            "description": "Mostra o XP atual e o nível de um usuário.",
            "usage": "/xp [usuário]",
            "examples": ["/xp", "/xp @Usuario123"]
        }
    }
)

# Export all elements
exports = [xp, xp_detailed_help]
