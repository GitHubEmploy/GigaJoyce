from asyncio import sleep
import sys, os
import shutil
from datetime import datetime
from pathlib import Path
from glob import glob
import discord
import asyncio
from discord import Embed, File
from discord import Intents
from discord.errors import HTTPException, Forbidden
from discord.ext import commands
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown,
                                  MissingPermissions, MissingRole, MissingAnyRole, NotOwner)
from discord.ext.commands import when_mentioned_or, CooldownMapping, BucketType
from git import Repo, rmtree
from ..db.db import MongoDBAsyncORM
import aiohttp
from dotenv import load_dotenv, dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient
import random
import math
import difflib
from time import timezone

OWNER_IDS = [322773637772083201, 840707271385284628, 930644246539665408]

COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

IGNORE_EXCEPTIONS = (
CommandNotFound, BadArgument, MissingPermissions, MissingRole, MissingAnyRole, MissingRequiredArgument, NotOwner)
message_cooldown = CooldownMapping.from_cooldown(1.0, 10, BucketType.user)

# bot = commands.Bot(command_prefix="s!", intents=intents)

config_keys = dotenv_values(".env")


async def get_prefix(bot, message):
    guild_data = await bot.db.find_one("guilds", {"guild_id": message.guild.id})
    if not guild_data or "prefix" not in guild_data:
        default_prefix = "j!"
        await bot.db.insert_one("guilds", {"guild_id": message.guild.id, "prefix": default_prefix})
        return when_mentioned_or(default_prefix)(bot, message)
    
    return when_mentioned_or(guild_data["prefix"])(bot, message)



async def get_prefix_message(message):
    guild_data = await bot.db.find_one("guilds", {"guild_id": message.guild.id})
    return guild_data["prefix"] if guild_data else "j!"


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog pronto")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])



class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()
        intents = Intents.default()
        intents.message_content = True
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        # Inicializa a conexão com o MongoDB
        self.db = MongoDBAsyncORM(uri=config_keys["MONGODB_TOKEN"], db_name="dbUser")

        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=intents,
            application_id="1273755708164280381"
        )

    async def setup(self):
        print(f"That's the cog list: {COGS}")
        for cog in COGS:
            await self.load_extension(f'lib.cogs.{cog}')
            print(f"{cog} cog loaded")
        print("Setup finished")
        
    async def update_db(self):
        
        # Get all guild IDs that are currently in the database
        guild_ids = [guild.id for guild in self.guilds]
        existing_guilds = await self.db.find("guilds", {"guild_id": {"$in": guild_ids}})
        existing_guild_ids = {guild['guild_id'] for guild in existing_guilds}

        # Create a list of guilds that are not yet in the database
        guild_insertions = [{"guild_id": guild.id} for guild in self.guilds if guild.id not in existing_guild_ids]

        # Insert the new guilds into the database
        if guild_insertions:
            await self.db.insert_many("guilds", guild_insertions)
        

        for guild in self.guilds:
            for member in guild.members:
                if not member.bot:

                    existing_user = await self.db.find_one("users", {"user_id": member.id})
                    if not existing_user:

                        await self.db.insert_one("users", 
                                                 {"user_id": member.id, 
                                                  "xp": 0, 
                                                  "coins": 0,
                                                  "avatar": None,
                                                  "bg_image": None,
                                                  "about": None,
                                                  })


    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.setup()

    def run(self, version):
        self.VERSION = version
        self.TOKEN = config_keys["BOT_TOKEN"]

        print("Running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if self.ready:
            if ctx.command is not None and ctx.guild is not None:
                await self.invoke(ctx)
        else:
            pass

    async def on_connect(self):
        await self.update_db()
        print("Bot connected")

    async def on_disconnect(self):
        print("Bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_comand_error":
            await args[0].send("Something got wrong `on_command_error`.")
        
        await self.stdout.send("Something got wrong.\n\n"
                               f"```\n{args}```")
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, asyncio.TimeoutError):
            await ctx.send("React time ended.")
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"This command is in cooldown. Try again after {exc.retry_after:,.2f}s")
        elif hasattr(exc, "original"):
            if isinstance(exc.original, Forbidden):
                await ctx.send("I don't have permission to do this.")
            else:
                raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.stdout = self.get_channel(1274786203211927723)
            print(f"Este é o stdout: {self.stdout}")
            self.scheduler.start()
            await self.update_db()

            while not self.cogs_ready.all_ready():
                await asyncio.sleep(0.5)

            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="TechJoyce"))
            
            print('Logged in as {0.user}'.format(self))    # Lets you know when the bot is online
            try:
                synced = await self.tree.sync()
                print(f"Synced {len(synced)} command(s)")
            except Exception as e:
                print(e)
            await self.stdout.send("I'm online!")
            self.GPT_KEY = config_keys["GPT_KEY"]
            self.ready = True
            print("Bot pronto")
        else:
            await self.stdout.send("My system fell, but I reconnecteded.")
            print("Bot Reconectado")

    async def on_message(self, message):
        if not message.author.bot:
            
            # Check if the message's channel is allowed for XP gain
            allowed_channel = await self.db.find_one("xp_allowed_channels", {"guild_id": message.guild.id, "channel_id": message.channel.id})
            
            if allowed_channel:
                await self.add_xp(message.author, message.guild, message)
            
            # prefix = await get_prefix_message(message)
            message_lower = message.content.lower()
            gptInit = ["joyce, ", "joyce: ", "hey, joyce: "]
            if message_lower.startswith(tuple(gptInit)):
                idg = await self.db.find_one("channels", {"guild_id": message.guild.id, "name": "chatbot"})
                
                if not idg:
                    await message.channel.send(f"Please configure a channel to use the chatbot function")
                elif idg.get("channel_id") != message.channel.id:
                    await message.channel.send(f"Please use AI functions in chat <#{str(idg.get('channel_id'))}>")
                elif idg.get("channel_id") == message.channel.id:
                    for prefix in gptInit:
                        if message_lower.removeprefix(prefix) != message_lower:
                            message_lower = message_lower.removeprefix(prefix)
                    
                    bucket = message_cooldown.get_bucket(message)
                    retry_after = bucket.update_rate_limit()
                    if retry_after:
                        await message.reply(f"Go slowly my dear. Try again after {retry_after}s.", delete_after=10)
                    else:
                        response = await gpt_response(self.gpt4f, 1, message_lower)
                        await message.reply(response)
            else:
                await self.process_commands(message)


    async def add_xp(self, user, guild, message):
        """
        Add XP to a user in a specific guild, check for role updates based on XP.
        :param user: The user gaining XP.
        :param guild: The guild where the XP is being added.
        :param message: The message that the user sent.
        """
        # Anti-spam measures
        if len(message.content) < 5:
            return  # Ignore very short messages

        user_data = await self.db.find_one("users", {"user_id": user.id, "guild_id": guild.id})

        if user_data:
            # Check if the message is similar to the last message sent by the user
            last_message = user_data.get("last_message", "")
            similarity = difflib.SequenceMatcher(None, last_message, message.content).ratio()
            if similarity > 0.9:
                return  # Ignore repeated or very similar messages

            # Cooldown to prevent too frequent XP gain
            last_xp_time = user_data.get("last_xp_time", None)
            if last_xp_time and (datetime.now(time.timezone.utc) - last_xp_time).total_seconds() < 60:
                return  # Ignore if the last XP gain was less than a minute ago

        # Determine XP gain using a more challenging formula
        base_xp_gain = random.randint(10, 20)  # Smaller base range to increase difficulty
        user_level = user_data["level"] if user_data else 1
        xp_gain = base_xp_gain + math.ceil(base_xp_gain * (user_level ** 0.5))  # More challenging XP gain

        # If no user data exists, initialize it
        if not user_data:
            user_data = {
                "user_id": user.id,
                "guild_id": guild.id,
                "xp": 0,
                "level": 1,
                "coins": 0,
                "avatar": None,
                "bg_image": None,
                "about": None,
                "last_message": message.content,
                "last_xp_time": datetime.now(timezone.utc)
            }
            await self.db.insert_one("users", user_data)
        else:
            # Update the last message and XP time
            await self.db.update_one(
                "users",
                {"user_id": user.id, "guild_id": guild.id},
                {
                    "$set": {
                        "last_message": message.content,
                        "last_xp_time": datetime.now(timezone.utc)
                    }
                }
            )

        # Update the user's XP
        new_xp = user_data["xp"] + xp_gain
        new_level = user_data["level"]
        
        # Implementing a more challenging leveling curve
        xp_needed_for_next_level = math.ceil(100 * (new_level ** 1.5))
        if new_xp >= xp_needed_for_next_level:
            new_level += 1
            new_xp = new_xp - xp_needed_for_next_level
            await user.send(f"Congratulations! You've leveled up to level {new_level}!")

        await self.db.update_one(
            "users",
            {"user_id": user.id, "guild_id": guild.id},
            {
                "$set": {
                    "xp": new_xp,
                    "level": new_level
                }
            }
        )

        # Check for role updates based on XP
        await self.check_and_update_roles(user, guild, new_xp)

    async def check_and_update_roles(self, user, guild, xp):
        """
        Check the user's XP against the guild's role requirements and update their roles accordingly.
        :param user: The user whose XP is being checked.
        :param guild: The guild where the XP is being checked.
        :param xp: The user's current XP.
        """
        # Fetch the role requirements from the database
        role_requirements = await self.db.find("role_requirements", {"guild_id": guild.id})
        
        if not role_requirements:
            return  # No role requirements set for this guild

        # Sort roles by XP requirement in descending order to assign the highest role possible
        role_requirements.sort(key=lambda r: r["xp_required"], reverse=True)

        new_role = None
        for role_requirement in role_requirements:
            if xp >= role_requirement["xp_required"]:
                new_role = guild.get_role(role_requirement["role_id"])
                break

        if not new_role:
            return  # No new role to assign

        # Assign the new role and remove any previous XP-based roles
        current_roles = user.roles
        xp_roles = [guild.get_role(r["role_id"]) for r in role_requirements if guild.get_role(r["role_id"]) in current_roles]
        
        try:
            await user.add_roles(new_role)
            for role in xp_roles:
                if role != new_role:
                    await user.remove_roles(role)

            await user.send(f"Congratulations! You've earned a new role: {new_role.name}")
        except discord.Forbidden:
            # Handle the case where the bot doesn't have permission to manage roles
            await self.log_channel.send(f"Failed to assign role {new_role.name} to {user.mention} due to missing permissions.")
        
async def gpt_response( gpt , mode, prompt):
    if mode == 2:

        response = gpt.images.generate(
            model="gemini",
            prompt = prompt
        )
        return response.data[0].url
    elif mode == 1:
        response = gpt.chat.completions.create(
            model= "gpt-3.5-turbo",
            messages= [
                {"role": "system",
                    "content": "Your name is Joyce and you are an elf with more than 500 years of life who lives in a fantasy world. You are a librarian and have access to all knowledge discovered by humanity in the real world. I want you to always respond as if you were talking to an adventurer."},
                {"role": "user",
                    "content": prompt}

            ])
        return response.choices[0].message.content  


bot = Bot()


