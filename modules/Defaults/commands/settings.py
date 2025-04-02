import discord
from discord import app_commands
from discord.ext import commands
from utils.InteractionView import InteractionView
from settings.Setting import Setting
import logging
from fuzzywuzzy import process
from shared.types import ExtendedClient


class SettingsCommand(commands.Cog):
    """
    Comando de configurações para visualizar e editar configurações do servidor e do usuário.
    """

    def __init__(self, bot: ExtendedClient):
        self.bot: ExtendedClient = bot
        self.logger = logging.getLogger("Settings")

    @app_commands.command(name="settings", description="Shows all server settings")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(setting="Name of the setting to search")
    async def settings_command(
        self, interaction: discord.Interaction, setting: str
    ):
        guild_id = interaction.guild.id if interaction.guild else None
        translate = await self.bot.translator.get_translator(guild_id=guild_id,module_name="Defaults")

        if not interaction.guild:
            await interaction.response.send_message(
                translate('settings.error.guild_only'), ephemeral=True
            )
            return

        guild = await self.bot.guild_manager.fetch_or_create(interaction.guild_id)

        # self.logger.info(f"Guild: {guild}")
        # self.logger.info(f"Guild.settings {guild.settings}")
        
        guild_setting = guild.settings.get(setting)
        if not guild_setting:
            await interaction.response.send_message(
                translate("settings.error.not_found"), ephemeral=True
            )
            return

        # Criar InteractionView e executar lógica
        view = InteractionView(
            interaction=interaction,
            channel=interaction.channel,
            client=self.bot,
            timeout=4 * 60 * 1000,
            filter_func=lambda i: i.user.id == interaction.user.id,
        )

        result = await guild_setting.run(view)
        
        if result is None:  # Se o resultado for inválido
            await interaction.edit_original_response(
                translate("settings.error.invalid_value"),
                ephemeral=True,
            )
            return
        
        guild_setting.value = result
        
        await guild_setting.save(self.bot, guild, guild_setting)
        
        if guild.id in self.bot.setting_cache:
            self.bot.setting_cache[guild.id][guild_setting.id] = guild_setting
        else:
            self.bot.setting_cache[guild.id] = {guild_setting.id: guild_setting}
        
        if guild_setting.id == "language":
            self.bot.logger.info(f"Atualizando Cache Guild: {guild_setting.value}")
            self.bot.translator.update_language_cache(interaction.guild_id, guild_setting.value)
       
        await interaction.edit_original_response(
            content=translate("settings.success.updated")
        )

    @staticmethod
    def _on_view_end(view: InteractionView, reason: str, translator):
        if reason == "time":
            view.update(
                {
                    "embeds": [],
                    "components": [],
                    "content": translator("settings.error.timeout"),
                }
            )

    @settings_command.autocomplete("setting")
    async def settings_autocomplete(
        self, interaction: discord.Interaction, current: str
    ):
        if not interaction.guild:
            return [
                app_commands.Choice(
                    name="Guild-only command. No settings available.", value="null"
                )
            ]

        guild_id = interaction.guild.id
        language = await self.bot.translator.get_language(guild_id=guild_id)
        
        translate = self.bot.translator.get_translator_sync(language=language, module_name="Defaults")
        
        guild = await self.bot.guild_manager.fetch_or_create(guild_id=guild_id)

        # Traduz o nome de cada configuração
        guild_settings = [
            {
                "name": translate("settings.autocomplete.guild_setting", name=self.bot.translator.get_translator_sync(language=language, module_name=s.module_name)(s.name)),
                "value": s.id,
            }
            for s in guild.settings.values()
        ]

        # Realiza a busca e cria as escolhas do autocomplete
        search_results = process.extract(
            current, [s["name"] for s in guild_settings], limit=23
        )
        choices = [
            app_commands.Choice(name=setting["name"], value=setting["value"])
            for setting in guild_settings
            if any(r[0] == setting["name"] for r in search_results)
        ]

        return choices



exports = [SettingsCommand]
