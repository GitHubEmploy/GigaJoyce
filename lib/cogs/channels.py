import typing
import discord
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, has_permissions, cooldown, is_owner
from discord import Embed, app_commands
from datetime import datetime
import json
from ..db import db


class Channels(Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('data/db/emojispersonalizados.json', 'rb') as j:
            self.emojis_personalizados = json.load(j)
            
    async def channel_autocomplete(
        self, 
        interaction: discord.Interaction,
        current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []

        for channel in interaction.guild.channels:
            if current.lower() in channel.name.lower():

                data.append(app_commands.Choice(name=channel.name, value=str(channel.id )))
        return data[:10]
    
    async def options(
        self, 
        interaction: discord.Interaction,
        current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        options = {
            "Drive": "drive",
            "Log": "log",
            "Log ban": "logban",
            "Vent": "vent",
            "Suggestion": "suggestion",
            "ChatBot": "chatbot"
        }
        for option in list(options.keys()):
            if current.lower() in option.lower():
                value = options[option]
                data.append(app_commands.Choice(name=option, value=value))
        return data
            
    @app_commands.command(name='set')
    @app_commands.autocomplete(option=options)
    @has_permissions(manage_channels=True)
    async def set_channel(self, interaction: discord.Interaction, option: str, canal: discord.TextChannel):
        channelId = int(canal.id)
        emoji = self.emojis_personalizados
        
        verify = self.bot.get_channel(channelId)

        if not verify:
            await interaction.response.send_message(
                f"<:fazeoq:716689988770594896> Não encontrei nenhum chat com o ID: **{channelId}**.\n"
                "**Verifique se o ID está certo.**", ephemeral=True
            )
        elif canal.guild.id != interaction.guild.id:
            await interaction.response.send_message(
            f"{emoji["angry"]}  I can't set a channel from another server.", ephemeral=True
            )

        else:

            channeld = await self.bot.db.find_one("channels", {"guild_id": interaction.guild.id, "name": option})

            if channeld is None:

                await self.bot.db.insert_one("channels", {
                    "guild_id": interaction.guild.id,
                    "name": option,
                    "channel_id": channelId
                })
            else:
                # Atualiza o canal existente
                await self.bot.db.update_one(
                    {"guild_id": interaction.guild.id, "name": option},
                    {"$set": {"channel_id": channelId}}
                )

            await interaction.response.send_message(
                f"<a:verificado_preto:824398284058656848> The {option} channel has been set to <#{channelId}>.", ephemeral=True
            )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("channels")


async def setup(bot):
    await bot.add_cog(Channels(bot))
