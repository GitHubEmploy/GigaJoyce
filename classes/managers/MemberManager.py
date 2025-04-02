from typing import List, Dict, Any, Optional
from discord import Guild as DiscordGuild, Member as GuildMember
from discord.ext.commands import Bot
from discord.ext.commands.errors import CommandError
from classes.structs.Member import Member
from classes.structs.Guild import Guild
from settings.Setting import Setting
from logging import Logger
from collections import defaultdict
from asyncio import Lock as AsyncLock
from shared.types import ExtendedClient

async def get_guilds(client: ExtendedClient, guilds: List[str]) -> List[Guild]:
    guild_array: List[Guild] = []
    for guild_id in guilds:
        if any(guild_obj.guild.id == int(guild_id) for guild_obj in guild_array):
            continue
        guild_array.append(await client.guild_manager.fetch_or_create(guild_id))
    return guild_array

async def get_all_settings(client: ExtendedClient, member_data: Any, guild: DiscordGuild, logger: Logger, user: GuildMember):
    settings = [setting for module in client.modules.values() for setting in module.user_settings]
    settings_map: Dict[str, Setting[Any]] = {}

    for original_setting in settings:
        setting = original_setting.clone()
        setting.save = original_setting.save
        setting.load = original_setting.load
        setting.parse = original_setting.parse
        setting.parse_to_database = original_setting.parse_to_database
        setting.condition = original_setting.condition

        setting_data = member_data.settings.get(setting.id)

        if setting.load:
            setting.value = await setting.load(guild, member_data, user)
        elif setting_data:
            if setting.parse:
                setting.value = await setting.parse(setting_data, client, member_data, guild, user)
            else:
                setting.value = setting_data
        settings_map[setting.id] = setting

    return settings_map

class MemberManager:
    def __init__(self, client: ExtendedClient, logger: Logger):
        self.client = client
        self.logger = logger

    async def fetch(self, member_id: str, guild_id: str) -> Member:
        member_id = str(member_id)
        guild_id = str(guild_id)
        if self.client.global_lock.is_locked():
            await self.client.global_lock.acquire()

        member_profile = await self.client.db.members.find_one({"id": member_id, "guildId": guild_id})
        if not member_profile:
            raise CommandError("No member profile!")

        guild_obj = await self.client.guild_manager.fetch_or_create(guild_id)
        if not guild_obj:
            raise CommandError("No guild found with the ID!")

        member = await guild_obj.guild.fetch_member(int(member_id))
        if not member:
            raise CommandError("No member!")

        settings = await get_all_settings(self.client, member_profile, guild_obj.guild, self.logger, member)
        return Member(self.client, member, guild_obj, settings, member_profile)

    async def fetch_or_create(self, member_id: str, guild_id: str) -> Member:
        guild_id = str(guild_id)
        member_id = str(member_id)
        if self.client.global_lock.is_locked():
            await self.client.global_lock.acquire()

        self.logger.debug(f"Fetching member {member_id} from guild {guild_id}")

        member_profile = await self.client.db.members.find_one({"id": member_id, "guildId": guild_id})
        guild_obj = await self.client.guild_manager.fetch_or_create(guild_id)
        if not guild_obj:
            raise CommandError("No guild!")

        if not member_profile:
            member_profile = {"id": member_id, "guildId": guild_id}
            await self.client.db.members.insert_one(member_profile)

        member = await guild_obj.guild.fetch_member(int(member_id))
        if not member:
            await self.client.db.members.delete_one({"id": member_id, "guildId": guild_id})
            raise CommandError("No member!")

        settings = await get_all_settings(self.client, member_profile, guild_obj.guild, self.logger, member)
        return Member(self.client, member, guild_obj, settings, member_profile)

    async def delete(self, member_id: str, guild_id: str):
        member_id = str(member_id)
        guild_id = str(guild_id)
        if self.client.global_lock.is_locked():
            await self.client.global_lock.acquire()

        member_profile = await self.client.db.members.find_one_and_delete({"id": member_id, "guildId": guild_id})
        if not member_profile:
            raise CommandError("No member profile!")

        return member_profile

    async def create(self, member_id: str, guild_id: str) -> Member:
        member_id = str(member_id)
        guild_id = str(guild_id)
        if self.client.global_lock.is_locked():
            await self.client.global_lock.acquire()

        existing_member = await self.client.db.members.find_one({"id": member_id, "guildId": guild_id})
        if existing_member:
            raise CommandError("Member already exists!")

        member_profile = {"id": member_id, "guildId": guild_id}
        await self.client.db.members.insert_one(member_profile)

        guild_obj = await self.client.guild_manager.fetch_or_create(guild_id)
        if not guild_obj:
            raise CommandError("No guild!")

        member = await guild_obj.guild.fetch_member(int(member_id))
        if not member:
            await self.client.db.members.delete_one({"id": member_id, "guildId": guild_id})
            raise CommandError("No member!")

        settings = await get_all_settings(self.client, member_profile, guild_obj.guild, self.logger, member)
        return Member(self.client, member, guild_obj, settings, member_profile)

    async def find_or_create_profile(self, member_id: str, guild_id: str) -> Any:
        member_id = str(member_id)
        guild_id = str(guild_id)
        if self.client.global_lock.is_locked():
            await self.client.global_lock.acquire()

        member_profile = await self.client.db.members.find_one({"id": member_id, "guildId": guild_id})
        if not member_profile:
            member_profile = {"id": member_id, "guildId": guild_id}
            await self.client.db.members.insert_one(member_profile)

        return member_profile

    async def find_by_kv(self, filter: Dict[str, Any]) -> List[Member]:
        if self.client.global_lock.is_locked():
            await self.client.global_lock.acquire()

        member_profiles = await self.client.db.members.find(filter).to_list(length=None)
        if not member_profiles:
            raise CommandError("No member profiles!")

        guild_ids = list(set(profile["guildId"] for profile in member_profiles))
        guild_array = await get_guilds(self.client, guild_ids)

        member_array: List[Member] = []
        for guild_obj in guild_array:
            member_ids = [profile["id"] for profile in member_profiles if profile["guildId"] == str(guild_obj.guild.id)]
            members = await guild_obj.guild.fetch_members(user_ids=member_ids)
            for member in members:
                member_profile = next((profile for profile in member_profiles if profile["id"] == str(member.id)), None)
                settings = await get_all_settings(self.client, member_profile, guild_obj.guild, self.logger, member)
                member_array.append(Member(self.client, member, guild_obj, settings, member_profile))

        return member_array
