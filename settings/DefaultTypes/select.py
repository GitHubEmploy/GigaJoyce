from discord import Embed, Interaction, ButtonStyle, ActionRow, SelectOption
from discord.ui import Select, View
from typing import List, Optional, Dict, Any
from utils.InteractionView import InteractionView
from settings.Setting import Setting


class SelectSetting(Setting[str]):
    """
    A setting that allows the user to select one option from a predefined list.
    """

    def __init__(
        self,
        name: str,
        description: str,
        id: str,
        options: List[Dict[str, str]],  # Cada opção será um dicionário com label e value
        value: Optional[str] = None,
        max_values: Optional[int] = 1,
        min_values: Optional[int] = 1,
        color: str = "#ffffff",
        permission: Optional[int] = None,
        locales: Optional[bool] = False,
        module_name: Optional[str] = None
    ):
        super().__init__(name=name, description=description, locales=locales, module_name=module_name, id=id, type_="select")
        self.options = options 
        self.value = value
        self.max_values = max_values
        self.min_values = min_values
        self.color = color
        self.permission = permission
        self.locales = locales
        self.module_name = module_name

    async def run(self, view: InteractionView) -> str:
        """
        Runs the interactive session for selecting options.
        """
        guild_id = str(view.interaction.guild.id)
        translate = await view.client.translator.get_translator(guild_id=guild_id)

        name, description, kwargs = self.name, self.description, self.kwargs

        if self.module_name and self.locales:
            translate_module = await view.client.translator.get_translator(guild_id=guild_id, module_name=self.module_name)
            name, description, kwargs = self.apply_locale(translate_module=translate_module)

        # Criar embed para exibição
        embed = Embed(
            title=translate("select_setting.title", setting_name=name),
            description=translate("select_setting.description", description=description),
            color=int(self.color.lstrip("#"), 16),
        )

        # Criar opções para o menu de seleção
        options = [
            SelectOption(label=option["label"], value=option["value"])
            for option in self.options
        ]

        # Criar Select
        select = Select(
            placeholder=translate("select_setting.placeholder"),
            options=options,
            max_values=1,  # Seleção única
            min_values=1,
            custom_id="select_option",
        )

        # Criar View
        select_view = View()
        select_view.add_item(select)

        await view.update(embeds=[embed], components=select_view.children)

        async def handle_select(inter: Interaction):
            selected_values = inter.data["values"]
            self.value = selected_values[0]  # Garantir que seja uma string
            embed.description = translate("select_setting.selected", selected=", ".join(selected_values))
            await inter.response.edit_message(embeds=[embed], view=None)
            view.stop()

        # Adicionar o callback ao Select
        select.callback = handle_select

        # Esperar a interação
        await view.wait()

        if not self.value:
            raise TimeoutError(translate("select_setting.timeout_error"))

        return self.value

    def parse_to_database(self, value: str) -> str:
        """
        Parse the value to a database-friendly format.
        """
        if not isinstance(value, str):
            raise ValueError(f"Expected a string for database storage, got {type(value).__name__}")
        return value
    
    def parse_from_database(self, config: Any) -> str:
        """
        Parse the value from a database configuration.
        """
        return config

    def parse_to_field(self, value: str) -> str:
        """
        Parse the value to a displayable string format.
        """
        label = next((option["label"] for option in self.options if option["value"] == value), "N/A")
        return label

    # def clone(self) -> "SelectSetting":
    #     """
    #     Clone the current instance.
    #     """
    #     return SelectSetting(
    #         name=self.name,
    #         description=self.description,
    #         id=self.id,
    #         options=self.options,
    #         value=self.value,
    #         max_values=self.max_values,
    #         min_values=self.min_values,
    #         color=self.color,
    #         locales=self.locales,
    #         module_name=self.module_name
    #     )
