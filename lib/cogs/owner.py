from datetime import datetime
from discord import Embed, File
from discord.ext.commands import Cog
from discord.ext.commands import command, is_owner, NotOwner, guild_only, Context, Greedy
from typing import Literal, Optional
import requests
import discord
import psutil
from pathlib import Path
import shutil
import os
import sys
import json
from ..db import db
from glob import glob
import os
from asyncio import sleep

COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
def get_prefix(message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)

    return prefix

def is_open(path):
    for proc in psutil.process_iter():
        try:
            files = proc.open_files()
            if files:
                for _file in files:
                    if _file.path == path:
                        return True, proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as err:
            pass
    return False, proc

class Owner(Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('data/db/emojispersonalizados.json', 'rb') as j:
            self.emojis_personalizados = json.load(j)
            
    @command()
    @guild_only()
    @is_owner()
    async def sync(self, ctx, guilds: Optional[int] = None):
        if not guilds:
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            await ctx.send(
                f"Synced {len(synced)} commands in {ctx.guild.name}"
            )     
        else:
            synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands globally"
            )


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("owner")


async def setup(bot):
    await bot.add_cog(Owner(bot))