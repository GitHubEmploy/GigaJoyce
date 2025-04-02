from discord import (
    Embed,
    ButtonStyle,
    Interaction,
    TextChannel,
)
from discord.ui import Button
from typing import Optional, Any
from utils.InteractionView import InteractionView
from settings.Setting import Setting
import asyncio


class NumberSetting(Setting[int]):
    """
    A setting that allows for configuring a numerical value interactively.
    """

    def __init__(
        self,
        name: str,
        description: str,
        id: str,
        value: Optional[int] = None,
        minValue: Optional[int] = float('-inf'),
        maxValue: Optional[int] = float('inf'),
        color: Optional[str] = "#ffffff",
        locales: Optional[bool] = False,
        module_name: Optional[str] = None,
    ):
        super().__init__(name=name, description=description, locales=locales, module_name=module_name, id=id, type_="number")
        self.value = value
        self.minValue = minValue
        self.maxValue = maxValue
        self.color = color
        self.locales = locales
        self.module_name = module_name

    async def run(self, view: InteractionView) -> int:
        """
        Runs the interactive session for configuring the numerical setting.
        """
        guild_id = str(view.interaction.guild.id)
        translate = await view.client.translator.get_translator(guild_id=guild_id)

        name, description, kwargs = self.name, self.description, self.kwargs

        if self.module_name and self.locales:
            translate_module = await view.client.translator.get_translator(guild_id=guild_id, module_name=self.module_name)
            name, description, kwargs = self.apply_locale(translate_module=translate_module)

        def update_embed(new_value=None):
            """
            Updates the embed to reflect the current or new value.
            """
            embed = Embed(
                title=translate("number_setting.title", setting_name=name),
                description=description,
                color=int(self.color.lstrip("#"), 16),
            )
            embed.add_field(
                name=translate("number_setting.current_value"),
                value=str(self.value) if self.value is not None else translate("number_setting.not_defined"),
                inline=False,
            )
            if new_value is not None:
                embed.add_field(
                    name=translate("number_setting.new_value"),
                    value=str(new_value),
                    inline=False,
                )
            return embed

        embed = update_embed()
        view.clear_items()

        # Botão para definir o valor
        set_button = Button(
            label=translate("number_setting.set_value"),
            custom_id="set_value",
            style=ButtonStyle.primary,
        )

        async def handle_set(inter: Interaction):
            """
            Handles setting a new numerical value.
            """
            await inter.response.defer()
            embed.description = translate("number_setting.enter_value")
            await view.update(embed=embed, components=[])

            channel = inter.channel  # Garantir que estamos em um canal válido
            if not isinstance(channel, TextChannel):
                raise ValueError("Invalid channel type for awaiting messages.")

            try:
                def check(msg):
                    return msg.author == inter.user and msg.channel == channel

                message = await view.client.wait_for("message", timeout=60.0, check=check)
                number = int(message.content.strip())

            except ValueError:
                embed.description = translate("number_setting.invalid_number")
                await view.update(embed=embed, components=[])
                return
            except asyncio.TimeoutError:
                embed.description = translate("number_setting.timeout")
                await view.update(embed=embed, components=[])
                raise TimeoutError(translate("number_setting.timeout_error"))

            if not (self.minValue <= number <= self.maxValue):
                embed.description = translate(
                    "number_setting.value_out_of_bounds",
                    value=number,
                    minValue=self.minValue,
                    maxValue=self.maxValue,
                )
                await view.update(embed=embed, components=[])
                return

            # Atualiza o embed com o novo valor
            self.value = number
            final_embed = update_embed(new_value=number)
            await view.update(embed=final_embed, components=[])
            view.stop()
            return number

        set_button.callback = handle_set
        view.add_item(set_button)

        # Enviar o embed inicial usando `view.update`
        await view.update(embed=embed, components=[set_button])

        await view.wait()

        if self.value is None:
            embed.description = translate("number_setting.timeout")
            await view.update(embed=embed, components=[])
            raise TimeoutError(translate("number_setting.timeout_error"))

        return self.value

    def parse_to_database(self, value: int) -> int:
        """
        Parse the numerical value for database storage.
        """
        return value

    def parse_from_database(self, config: Any) -> int:
        """
        Parse the numerical value from database format.
        """
        return int(config)

    def parse_to_field(self, value: int, translator: Optional[callable] = None) -> str:
        """
        Parse the value to a displayable string format.
        """
        return f"{translator('current_value')}: {value}"

    def clone(self) -> "NumberSetting":
        """
        Clone the current instance.
        """
        return NumberSetting(
            name=self.name,
            description=self.description,
            id=self.id,
            value=self.value,
            maxValue=self.maxValue,
            minValue=self.minValue,
            color=self.color,
        )
