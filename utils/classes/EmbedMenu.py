import discord
from discord.ui import Button, View
from discord.ext import commands
from typing import List, Union, Optional
from asyncio import TimeoutError


class EmbedMenu:
    def __init__(
        self,
        embed: discord.Embed,
        row: Union[discord.ActionRow, List[discord.ActionRow]],
        msg: discord.Message,
        author_id: str,
    ):
        """
        A class to manage an interactive embed menu.

        :param embed: The initial embed to display.
        :param row: The action rows (buttons) for the embed.
        :param msg: The message object representing the menu.
        :param author_id: The ID of the user allowed to interact with the menu.
        """
        self.embed = embed
        self.last = {"embed": embed, "row": row if isinstance(row, list) else [row]}
        self.row = self.last["row"]
        self.msg = msg
        self.channel = msg.channel
        self.author_id = author_id
        self.collector = None

    async def setup_collector(self, timeout: int = 60):
        """
        Set up the button interaction collector.

        :param timeout: The time (in seconds) before the menu automatically stops.
        """
        self.collector = discord.ui.View(timeout=timeout)

        # Add buttons from the action rows
        for row in self.row:
            for component in row.children:
                if isinstance(component, Button):
                    self.collector.add_item(component)

        def is_author(interaction: discord.Interaction) -> bool:
            return interaction.user.id == int(self.author_id)

        try:
            while True:
                interaction = await self.msg.wait_for("interaction", check=is_author, timeout=timeout)

                if interaction.data["custom_id"] == "return":
                    await interaction.response.defer()
                    await self.update_page(self.last["embed"], self.last["row"])
                else:
                    event_name = interaction.data["custom_id"].split("-")[0]
                    self.emit(event_name, interaction)

        except TimeoutError:
            self.emit("end", "time")

    async def update_page(self, embed: discord.Embed, row: Union[discord.ActionRow, List[discord.ActionRow]]):
        """
        Update the embed and action rows displayed in the menu.

        :param embed: The new embed to display.
        :param row: The new action rows (buttons).
        """
        self.last["embed"] = self.embed
        self.last["row"] = self.row
        self.embed = embed
        self.row = row if isinstance(row, list) else [row]

        # Update the message
        await self.msg.edit(embed=self.embed, view=self.collector if self.row else None)

    async def set_disabled(self, custom_id: str, disabled: bool):
        """
        Enable or disable a specific button.

        :param custom_id: The custom ID of the button to modify.
        :param disabled: Whether to disable (True) or enable (False) the button.
        """
        for row in self.row:
            for button in row.children:
                if isinstance(button, Button) and button.custom_id == custom_id:
                    button.disabled = disabled

        await self.update_page(self.embed, self.row)

    def stop(self):
        """
        Stop the menu and cleanup the collector.
        """
        if self.collector:
            self.collector.stop()
import discord
from discord.ui import Button, View
from discord.ext import commands
from typing import List, Union, Optional
from asyncio import TimeoutError


class EmbedMenu:
    def __init__(
        self,
        embed: discord.Embed,
        row: Union[discord.ActionRow, List[discord.ActionRow]],
        msg: discord.Message,
        author_id: str,
    ):
        """
        A class to manage an interactive embed menu.

        :param embed: The initial embed to display.
        :param row: The action rows (buttons) for the embed.
        :param msg: The message object representing the menu.
        :param author_id: The ID of the user allowed to interact with the menu.
        """
        self.embed = embed
        self.last = {"embed": embed, "row": row if isinstance(row, list) else [row]}
        self.row = self.last["row"]
        self.msg = msg
        self.channel = msg.channel
        self.author_id = author_id
        self.collector = None

    async def setup_collector(self, timeout: int = 60):
        """
        Set up the button interaction collector.

        :param timeout: The time (in seconds) before the menu automatically stops.
        """
        self.collector = discord.ui.View(timeout=timeout)

        # Add buttons from the action rows
        for row in self.row:
            for component in row.children:
                if isinstance(component, Button):
                    self.collector.add_item(component)

        def is_author(interaction: discord.Interaction) -> bool:
            return interaction.user.id == int(self.author_id)

        try:
            while True:
                interaction = await self.msg.wait_for("interaction", check=is_author, timeout=timeout)

                if interaction.data["custom_id"] == "return":
                    await interaction.response.defer()
                    await self.update_page(self.last["embed"], self.last["row"])
                else:
                    event_name = interaction.data["custom_id"].split("-")[0]
                    self.emit(event_name, interaction)

        except TimeoutError:
            self.emit("end", "time")

    async def update_page(self, embed: discord.Embed, row: Union[discord.ActionRow, List[discord.ActionRow]]):
        """
        Update the embed and action rows displayed in the menu.

        :param embed: The new embed to display.
        :param row: The new action rows (buttons).
        """
        self.last["embed"] = self.embed
        self.last["row"] = self.row
        self.embed = embed
        self.row = row if isinstance(row, list) else [row]

        # Update the message
        await self.msg.edit(embed=self.embed, view=self.collector if self.row else None)

    async def set_disabled(self, custom_id: str, disabled: bool):
        """
        Enable or disable a specific button.

        :param custom_id: The custom ID of the button to modify.
        :param disabled: Whether to disable (True) or enable (False) the button.
        """
        for row in self.row:
            for button in row.children:
                if isinstance(button, Button) and button.custom_id == custom_id:
                    button.disabled = disabled

        await self.update_page(self.embed, self.row)

    def stop(self):
        """
        Stop the menu and cleanup the collector.
        """
        if self.collector:
            self.collector.stop()
