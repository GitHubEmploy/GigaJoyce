from code import interact
from typing import Optional
from discord import Embed, Interaction, ButtonStyle
from discord.ui import Button
from utils.InteractionView import InteractionView
from settings.Setting import Setting


class BooleanSetting(Setting[bool]):
    """
    Represents a boolean setting that can be modified via interactions.
    """

    def __init__(self, name: str, description: str, id: str, value: Optional[bool] = None, color: str = "#ffffff", locales: Optional[bool] = False, module_name: Optional[str] = None):
        super().__init__(name=name, description=description, locales=locales, module_name=module_name, id=id, type_="boolean")
        self.value = value or False
        self.color = color
        self.locales = locales
        self.module_name = module_name

    async def run(self, view: InteractionView) -> bool:
        """
        Interactively modifies the boolean setting.
        """
        guild_id = str(view.interaction.guild.id)
        translate = await view.client.translator.get_translator(guild_id=guild_id)

        name, description, kwargs = self.name, self.description, self.kwargs

        if self.module_name and self.locales:
            translate_module = await view.client.translator.get_translator(guild_id=guild_id, module_name=self.module_name)
            name, description, kwargs = self.apply_locale(translate_module=translate_module)
            
        value = self.value
        embed = Embed(
            
            title=translate("boolean_setting.title", setting_name=name),
            description=description,
            color=int(self.color.lstrip("#"), 16)
        ).add_field(
            name=translate("current_value"),
            value=translate("enabled") if value else translate("disabled")
        )
        
        enable = Button(label=translate("enable"), custom_id="activate", style=ButtonStyle.secondary, disabled=value)
        disable = Button(label=translate("disable"), custom_id="deactivate", style=ButtonStyle.secondary, disabled=not value)

    
        async def button_callback(button_interaction: Interaction):
            await button_interaction.response.defer()
            nonlocal value
            value = not value
            view.stop()
            

        enable.callback = button_callback
        disable.callback = button_callback
        
        await view.update(embed=embed, components=[enable, disable])

        await view.wait()

        if not view.is_finished():
            # Handle timeout
            embed = Embed(
                title=translate("boolean_setting.title", setting_name=self.name),
                description=translate("timeout"),
                color=int(self.color.lstrip("#"), 16)
            )
            await view.update(embed=embed, components= [])

        return value
    
    def parse_to_database(self, value: bool) -> bool:
        """
        Prepares the channel for storage in the database.
        """
        return value

    # def clone(self) -> "BooleanSetting":
    #     """
    #     Returns a clone of the current setting.
    #     """
    #     return BooleanSetting(name=self.name, description=self.description, id=self.id, value=self.value, color=self.color)
