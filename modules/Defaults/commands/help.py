# help.py

import asyncio
from discord import app_commands, Embed, Interaction, ButtonStyle, SelectOption
from discord.ui import Button, Select
from utils.InteractionView import InteractionView
from typing import List, Dict, Optional
from shared.types import ExtendedClient
from discord.ext import commands


class HelpCommand(commands.Cog):
    def __init__(self, bot: ExtendedClient):
        self.bot = bot

    @app_commands.command(name="help", description="Shows all commands or information about a specific command.")
    @app_commands.describe(command="Command name to search for.")
    async def help_command(self, interaction: Interaction, command: Optional[str] = None):
        guild_id = interaction.guild.id if interaction.guild else None
        language = await self.bot.translator.get_language(guild_id)
        translate = self.bot.translator.get_module_translations("Defaults", language)
        

        if command:
            await self._send_command_description(interaction, command, language, translate)
        else:
            await self._send_modules_overview(interaction, language, translate)

    async def _send_command_description(self, interaction: Interaction, command_name: str, language: str, translate):
        command = self.bot.get_command(command_name)
        if not command:
            await interaction.response.send_message(translate("help.command_not_found"), ephemeral=True)
            return

        embed = Embed(
            title=f"{translate('help.command')}: {command.name}",
            description=command.description or translate("help.no_description"),
            color=0x4040F0,
        )
        embed.add_field(name=translate("help.how_to_use"), value=f"`/{command.name}`", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _send_modules_overview(self, interaction: Interaction, language: str, translate):
        modules = self.bot.modules
        embed = Embed(
            title=translate("help.modules"),
            color=0x4040F0,
        )
        for module_name, module in modules.items():
            embed.add_field(name=module_name, value=module.description or translate("help.no_description"), inline=True)

        # Criar opções para o menu seletor
        options = [
            SelectOption(label=module_name, value=module_name)
            for module_name in modules.keys()
        ]

        # Criar o seletor
        module_select = Select(
            placeholder=translate("help.select_module"),
            options=options,
            custom_id="module_select"
        )

        # Definir o callback para o seletor que emite um evento personalizado
        async def on_module_select(selected_interaction: Interaction):
            # Evita interações não autorizadas
            if not self._validate_interaction(view, selected_interaction):
                await selected_interaction.response.send_message("Você não pode usar este componente.", ephemeral=True)
                return
            selected_module_name = selected_interaction.data["values"][0]
            # Emite o evento 'module_select' com os parâmetros necessários
            view.emit("module_select", selected_interaction, selected_module_name)

        module_select.callback = on_module_select

        # Criar a view personalizada
        view = InteractionView(
            interaction=interaction,
            channel=interaction.channel,
            client=self.bot,
            ephemeral=True
        )

        # Adicionar o seletor à view
        view.add_item(module_select)

        # Registrar o listener para o evento 'module_select'
        view.on("module_select", lambda inter, mod_name: asyncio.create_task(
            self._send_module_commands(inter, mod_name, language, translate)
        ))

        # Registrar o listener para o evento 'end' caso precise realizar ações adicionais
        view.on("end", self._handle_view_end)

        # Enviar a mensagem com embed e view
        await view.update(embeds=[embed], components=[module_select])

    async def _send_module_commands(self, interaction: Interaction, module_name: str, language: str, translate):
        """
        Envia a lista de comandos dentro de um módulo específico.

        :param interaction: A interação do Discord.
        :param module_name: Nome do módulo selecionado.
        :param language: Idioma para tradução.
        :param translate: Função de tradução.
        """
        module = self.bot.modules.get(module_name)  # Certifique-se de que 'modules' é um dicionário no bot
        
        translateModule = self.bot.translator.get_module_translations(module_name, language)
        
        if not module:
            await interaction.response.send_message(translate("help.module_not_found"), ephemeral=True)
            return

        # Combine comandos de texto e comandos slash
        commands = {**module.commands["text"], **module.commands["slash"]}

        self.bot.logger.info(f"Comandos dentro do módulo {module_name}: {commands}")
        embed = Embed(
            title=f"{translate('help.commands_in_module')} {module_name}",
            description=translateModule(f"{module_name}.module_commands_description"),
            color=int(module.color.lstrip('#'), 16),  # Convertendo cor hexadecimal para int
        )
        
            
        for command_name, command in commands.items():
            translated_desc = translateModule(f"{command_name}.no_description")
            
            if translated_desc != f"{command_name}.no_description":
                command_value = translated_desc
            else:
                command_value = command.description
                
            embed.add_field(
                name=f"`/{command_name}`",
                value=command_value,
                inline=False
            )

        back_button = Button(label=translate("help.back"), style=ButtonStyle.primary, custom_id="back_to_modules")

        # Tente recuperar a view do registro; caso não exista, crie uma nova
        view = self.bot.view_registry.get(interaction.message.id)
        if view is None:
            view = InteractionView(
                interaction=interaction,
                channel=interaction.channel,
                client=self.bot,
                ephemeral=True
            )
            self.bot.view_registry[interaction.message.id] = view

        view.add_item(back_button)

        async def on_back_button_click(selected_interaction: Interaction):
            await self._send_modules_overview(selected_interaction, language, translate)

        back_button.callback = on_back_button_click

        await view.update(embeds=[embed], components=[back_button])


    async def _handle_view_end(self, reason: str):
        """
        Método opcional para lidar com o término da view.

        :param reason: Razão do término ('timeout', 'deleted', etc.).
        """
        self.bot.logger.debug(f"View ended for: {reason}")

    def _validate_interaction(self, view: InteractionView, interaction: Interaction) -> bool:
        """
        Valida se a interação pertence à view atual.

        :param view: A instância da InteractionView.
        :param interaction: A interação a ser validada.
        :return: True se for válida, False caso contrário.
        """
        return view.filter_func(interaction)


# Exportar o comando como uma lista
exports = [HelpCommand]
