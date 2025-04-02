from random import choice, randint
import discord
from typing import Optional
from datetime import datetime
from aiohttp import request
from discord import Member, Embed, app_commands
from discord.errors import HTTPException
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument, MissingRequiredArgument
from discord.ext.commands import command, cooldown, hybrid_command, is_owner
import json
from math import floor
from time import sleep

from ..db import db

def get_prefix(message):
	prefix = db.field("SELECT prefix FROM guilds WHERE guild_id = ?", message.guild.id)
	return prefix

async def gpt_response( gpt , mode, prompt):
    if mode == 2:

        response = gpt.images.generate(
            model="dall-e-3",
            prompt = prompt
        )
        return response.data[0].url
    elif mode == 0:
        response = gpt.chat.completions.create(
            model= "gpt-4-turbo",
            messages= [
                {"role": "system",
                    "content": "Seu nome é Sophia e você é uma elfa com mais de 500 anos de vida que vivem em um mundo fantasioso. Você é bibliotecária e tem acesso a todo conhecimento descoberto pela humanidade no mundo real. Quero que sempre responda como se tivesse falando com um aventureiro."},
                {"role": "user",
                    "content": prompt}

            ])
        return response.choices[0].message.content  
    elif mode == 1:
        response = gpt.chat.completions.create(
            model= "gpt-3.5-turbo",
            messages= [
                {"role": "system",
                    "content": "Seu nome é Sophia e você é uma elfa com mais de 500 anos de vida que vivem em um mundo fantasioso. Você é bibliotecária e tem acesso a todo conhecimento descoberto pela humanidade no mundo real. Quero que sempre responda como se tivesse falando com um aventureiro."},
                {"role": "user",
                    "content": prompt}

            ])
        return response.choices[0].message.content  

class Gpt(Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('data/db/emojispersonalizados.json', 'rb') as j:
            self.emojis_personalizados = json.load(j)
            
  
    @app_commands.command(name="chatbot", description="Faça perguntas para a Σοφία")
    @app_commands.choices(mode=[ 
                                # app_commands.Choice(name="gpt-4-turbo", value = 0),
                                app_commands.Choice(name="gpt-3-turbo", value = 1), 
                                # app_commands.Choice(name="imagem", value = 2)
                                ])
    @cooldown(1, 30, BucketType.user)
    async def chatbot(self, interaction: discord.Interaction, mode: int, question: str):
        emoji = self.emojis_personalizados
        idg = db.field('SELECT channel_id FROM channels WHERE guild_id =? AND name ="chatbot"', interaction.guild.id)
        
        if not idg:
            await interaction.response.send_message(f"{emoji['gatinho']}  Por favor, peça para que algum administrador configure um canal para utilizar a função de chatbot", ephemeral=True)
        elif idg != interaction.channel.id:
            await interaction.response.send_message(f"{emoji['gatinho']}  Por favor, use as funções de IA no chat <#{str(idg)}>", ephemeral=True)
        elif idg == interaction.channel.id:

            
            if mode == 1:
                gpt  = self.bot.gpt4f            
            else:
                if interaction.user.premium_since:
                    gpt = self.bot.gpt
                else:
                    await interaction.response.send_message(f"{emoji['okie']}  Você precisa dar pelo menos um **boost** no servidor antes de usar esta função.")
                    return 
            
            await interaction.response.defer()
            resposta = await gpt_response(gpt, mode, question )

            if resposta: 
                respostas = [resposta[n:n+2000] for n in range(0, len(resposta), 2000) ]
                
                for r in respostas: 
                    await interaction.followup.send(r)
                    sleep(0.5)
            else:
                await interaction.followup.send(f"Sinto muito meu nobre aventureiro. Infelizmente tive algum problema para acessar minha biblioteca")


        # personalidade = "Seu nome é Sophia e você é uma elfa com mais de 500 anos de vida que vivem em um mundo fantasioso. Você é bibliotecária e tem acesso a todo conhecimento descoberto. Agora me responda o seguinte: "
        # response = gpt.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     prompt=personalidade+prompt,
        #     max_tokens=50
        # )
        
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("gpt")


async def setup(bot):
	await bot.add_cog(Gpt(bot))
