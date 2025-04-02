import discord

async def on_interaction(interaction: discord.Interaction):
    """
    Handles interaction creation events, including slash commands and auto-complete handling.
    """
    if not interaction.guild:
        return  # Only process interactions in guilds

    if interaction.type == discord.InteractionType.application_command:
        command = interaction.client.tree.get_command(interaction.command.name)
        if not command:
            return  # Command not found

        if getattr(command, "disabled", False):
            await interaction.response.send_message(
                content="This command is temporarily disabled.", ephemeral=True
            )
            return

        module_name = getattr(command, "module", None)
        if not module_name:
            return

        module = interaction.client.get_cog(module_name)
        if not module:
            return

        try:
            # Execute middleware functions if any are defined
            for middleware_fn in getattr(interaction.client, "command_middleware", []):
                result = await middleware_fn(
                    client=interaction.client,
                    interaction=interaction,
                    profile=await fetch_profile(interaction),
                    guild=await fetch_guild(interaction),
                    module=module,
                    command=command,
                )
                if not result:
                    return

            # Execute the command
            await command.callback(interaction)

            # Log command execution
            interaction.client.logger.info(
                f"Command executed: {command.name}",
                extra={
                    "command": {
                        "name": command.name,
                        "module": module_name,
                    },
                    "guild": {
                        "name": interaction.guild.name,
                        "id": interaction.guild.id,
                    },
                    "user": {
                        "name": interaction.user.name,
                        "id": interaction.user.id,
                    },
                },
            )
        except Exception as e:
            interaction.client.logger.error(f"Error executing command {command.name}: {e}")
            await interaction.response.send_message(
                content="There was an error while executing this command!", ephemeral=True
            )

    elif interaction.type == discord.InteractionType.application_command_autocomplete:
        command = interaction.client.tree.get_command(interaction.command.name)
        if not command:
            return  # Command not found

        auto_complete_func = getattr(command, "autocomplete", None)
        if not auto_complete_func:
            await interaction.response.send_autocomplete_choices(
                [
                    discord.app_commands.Choice(
                        name="This command does not have auto-complete set up.",
                        value="null",
                    )
                ]
            )
            return

        try:
            # Run auto-complete function
            await auto_complete_func(interaction)
        except Exception as e:
            interaction.client.logger.error(f"Error in auto-complete for {command.name}: {e}")


async def fetch_profile(interaction: discord.Interaction):
    """
    Fetch the user profile for the interaction.
    """
    # Placeholder for fetching user profile
    return {}


async def fetch_guild(interaction: discord.Interaction):
    """
    Fetch the guild profile for the interaction.
    """
    # Placeholder for fetching guild data
    return {}


# Event dictionary for dynamic loading
event = {
    "event": "on_interaction",
    "func": on_interaction
}
