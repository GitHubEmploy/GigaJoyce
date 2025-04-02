import discord
from discord.ext import commands
import aiohttp
import os
import zipfile
import json

class EmojiDownloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="emojis")
    @commands.has_permissions(administrator=True)
    async def download_emojis(self, ctx):
        """Baixa todos os emojis do servidor e compacta em um arquivo ZIP."""
        if not ctx.guild:
            await ctx.send("Este comando só pode ser usado em um servidor.")
            return

        emojis = ctx.guild.emojis
        if not emojis:
            await ctx.send("Este servidor não possui emojis personalizados.")
        
            return
        print(f"Fui chamado")
        await ctx.send(f"Baixando os arquivos")
        folder_name = f"{ctx.guild.name}_emojis"
        zip_name = f"{folder_name}.zip"

        # Cria uma pasta para armazenar os emojis temporariamente
        os.makedirs(folder_name, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            for emoji in emojis:
                emoji_url = str(emoji.url)
                emoji_name = f"{emoji.name}.{'gif' if emoji.animated else 'png'}"
                file_path = os.path.join(folder_name, emoji_name)

                async with session.get(emoji_url) as response:
                    if response.status == 200:
                        with open(file_path, "wb") as f:
                            f.write(await response.read())

        # Compacta os arquivos em um ZIP
        with zipfile.ZipFile(zip_name, "w") as zipf:
            for root, _, files in os.walk(folder_name):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)

        # Envia o arquivo ZIP no canal
        await ctx.send(file=discord.File(zip_name))

        # Limpa os arquivos temporários
        for root, _, files in os.walk(folder_name):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(folder_name)
        os.remove(zip_name)

        await ctx.send("Download dos emojis concluído!")

    @commands.command(name="export_emojis")
    @commands.has_permissions(administrator=True)
    async def export_emojis(self, ctx):
        """
        Coleta todos os emojis do servidor e cria um JSON com seus nomes e códigos.
        """
        server_emojis = ctx.guild.emojis

        if not server_emojis:
            await ctx.send("This server doesn't have emojis!")
            return

        emoji_dict = {
            f":{emoji.name}:": str(emoji)  # str(emoji) já retorna o código no formato <nome:id>
            for emoji in server_emojis
        }

        # Salvar em um arquivo JSON local
        file_name = f"{ctx.guild.id}_emojis.json"
        with open(file_name, "w", encoding="utf-8") as json_file:
            json.dump(emoji_dict, json_file, ensure_ascii=False, indent=4)

        await ctx.send(
            f"The emojis have been exported successfully! Check the file`{file_name}`.",
            file=discord.File(file_name)
        )
exports = [EmojiDownloader]
