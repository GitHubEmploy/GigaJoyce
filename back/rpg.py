from random import choice, randint
import discord
from typing import Optional
from datetime import datetime, timezone
from aiohttp import request
from discord import Member, Embed, app_commands
from discord.errors import HTTPException
from discord.ext.commands import Cog, BucketType, GroupCog
from discord.ext.commands import BadArgument, MissingRequiredArgument
from discord.ext.commands import command, cooldown, hybrid_command, is_owner
import json

# from ..db import db


from PIL import Image, ImageDraw, ImageFont

def create_profile_image(background_path, avatar_path, username, xp, level, race, output_path):
    # Carrega a imagem de fundo e o avatar
    background = Image.open(background_path).convert("RGBA")
    avatar = Image.open(avatar_path).convert("RGBA")

    # Define a proporção do tamanho do avatar em relação ao background
    avatar_scale = 0.8  # Exemplo: o avatar é 1/8 da altura do background

    # Calcula o novo tamanho do avatar baseado na proporção definida
    new_avatar_height = int(background.height * avatar_scale)
    new_avatar_width = int((new_avatar_height / avatar.height) * avatar.width)
    avatar = avatar.resize((new_avatar_width, new_avatar_height))

    # Posição do avatar na imagem de fundo (ajuste conforme necessário)
    # Exemplo: posicionando o avatar no centro inferior do background
    avatar_position = (background.width // 2 - new_avatar_width // 2, 
                       background.height - new_avatar_height - 50)  # 50 pixels acima da borda inferior

    # Cria uma imagem "composta" com base no fundo
    background.paste(avatar, avatar_position, avatar)

    # Preparando para desenhar o texto
    draw = ImageDraw.Draw(background)
    font = ImageFont.load_default(size=50)  # Carrega a fonte padrão, ou especifique uma fonte de sua escolha
    i = 3
    # Informações do jogador
    text_position = (20, 20)  # Posição do texto no canto superior esquerdo
    draw.text(text_position, f"Username: {username}", (255, 255, 255), font=font)
    draw.text((text_position[0], text_position[1] + 20*i), f"XP: {xp}", (255, 255, 255), font=font)
    draw.text((text_position[0], text_position[1] + 40*i), f"Level: {level}", (255, 255, 255), font=font)
    draw.text((text_position[0], text_position[1] + 60*i), f"Raça: {race}", (255, 255, 255), font=font)

    # Salva a imagem composta
    background.save(output_path, "PNG")
    
def create_xp_bar(width, height, percentage, save_path):
    # Criar uma nova imagem com fundo transparente
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Definir cores
    background_color = (50, 50, 50)  # Cor de fundo, cinza escuro
    progress_color = (76, 175, 80)   # Cor de progresso, verde

    # Desenhar o fundo da barra de XP
    # draw.rectangle([0, 0, width, height], fill=background_color)
    
    # Calcular a largura do progresso
    progress_width = int((width * percentage) / 100)
    
    # Definir o raio para os cantos arredondados
    corner_radius = 40

    # Desenhar o fundo da barra de XP com cantos arredondados
    draw.rounded_rectangle([0, 0, width, height], radius=corner_radius, fill=background_color)

    # Desenhar a barra de progresso com cantos arredondados
    # A barra só será arredondada do lado esquerdo se o progresso for pequeno, e de ambos os lados se o progresso for completo.
    if progress_width > corner_radius:
        draw.rounded_rectangle([0, 0, progress_width, height], radius=corner_radius, fill=progress_color)
    else:
        # Se o progresso é muito pequeno, desenhar um retângulo normal para evitar distorção visual
        draw.rectangle([0, 0, progress_width, height], fill=progress_color)
    
    # Opcional: Adicionar texto
    try:
        # Tentar carregar uma fonte TTF/OTF
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        # Se não conseguir, usar a fonte padrão
        font = ImageFont.load_default()

    text = f"{percentage}%"
    # Calculando a caixa delimitadora do texto
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
    
    # Salvar a imagem
    image.save(save_path)

# Uso da função
create_xp_bar(300, 50, 75, "data/images/xp_bar.png")
    
bg = r"C:\Users\carlos23001\Documents\GithubProjects\sophia\data\images\background.png"
avatar = r"C:\Users\carlos23001\Documents\GithubProjects\sophia\data\images\elfo_masc.png"

# create_profile_image(bg, avatar, "elementare", 36000, 15, "Elfo", "data/images/elementare_pfp.png")

class Rpg(GroupCog, name="rpg"):
    def __init__(self, bot):
        self.bot = bot
        with open('data/db/emojispersonalizados.json', 'rb') as j:
            self.emojis_personalizados = json.load(j)
            
        with open('data/db/rpg_metadata.json', 'rb') as j:
            self.rpg_metadata = json.load(j)
  
    @app_commands.command(name="new-character", description="Create a new character")
    @app_commands.choices(sexo=[
        app_commands.Choice(name="Biotype 1", value=1),
        app_commands.Choice(name="Biotype 2", value=2),
        app_commands.Choice(name="Interbiotype", value=0)
    ])
    @app_commands.choices(race=[
        app_commands.Choice(name="Human", value=0),
        app_commands.Choice(name="Elf", value=1),
        app_commands.Choice(name="Wolf", value=2),
        app_commands.Choice(name="Dwarf", value=3)
    ])
    @app_commands.choices(avatar=[
        app_commands.Choice(name="Default 1", value=0),
        app_commands.Choice(name="Default 2", value=1)
    ])
    @app_commands.choices(kingdom=[
        app_commands.Choice(name="Mathematics Kingdom", value=1),
        app_commands.Choice(name="Physics Kingdom", value=2)
    ])
    async def character_register(self, interaction: discord.Interaction, name: str, sexo: int, race: int, avatar: int, kingdom: int):
        metadata = self.rpg_metadata
        user_id = interaction.user.id

        # Check how many characters the user already has in the database
        existing_characters = await self.bot.db.count_documents("characters", {"user_id": user_id})

        # Check if the user is boosting the server
        is_boosting = any(role.is_premium_subscriber() for role in interaction.user.roles)

        # If the user is not boosting and already has a character, deny creation of a new one
        if existing_characters > 0 and not is_boosting:
            await interaction.response.send_message("You can only create more than one character if you are boosting the server.", ephemeral=True)
            return

        # Insert a new character into the database
        character_data = {
            "user_id": user_id,
            "username": name,
            "kingdom": kingdom,
            "sexo": sexo,
            "avatar": avatar,
            "race": race,
            "xp": 0,
            "level": 0
        }
        await self.bot.db.insert_one("characters", character_data)
        await interaction.response.send_message("Character successfully created!")
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("rpg")


async def setup(bot):
	await bot.add_cog(Rpg(bot))
