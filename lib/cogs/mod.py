from asyncio import sleep
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional
from discord.ext.commands import MissingPermissions
from discord import Embed, Member, NotFound, Object, Webhook, app_commands
from discord.utils import find
from discord.ext.commands import Cog, Greedy, Converter, BucketType, GroupCog
from discord.ext.commands import CheckFailure, BadArgument, MissingRequiredArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions, is_owner, cooldown, hybrid_command
from discord.utils import get
from datetime import datetime, timezone
from collections import defaultdict
import json
import discord
import time



class Mod(Cog):
    def __init__(self, bot):
        with open('data/db/emojispersonalizados.json', 'rb') as j:
            self.emojis_personalizados = json.load(j)
        with open('data/db/emojisdefault.json', 'rb') as j:
            self.emojis_padrao = json.load(j)
        with open("data/db/roles.json", 'rb') as f:
            self.role = json.load(f)

        self.bot = bot

    @app_commands.command(name="ban", description="Ban a member")
    async def ban_membro(self, interaction: discord.Interaction, member: discord.Member, duration: Optional[int] = None, reason: Optional[str] = "It was not informed"):
        await self.handle_moderation_action(interaction, member, reason, action="ban", duration=duration)

    @app_commands.command(name="kick", description="Kick a member")
    async def kick_membro(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = "It was not informed"):
        await self.handle_moderation_action(interaction, member, reason, action="kick")

    @app_commands.command(name="mute", description="Mute a member")
    async def mute_membro(self, interaction: discord.Interaction, member: discord.Member, duration: Optional[int] = None, reason: Optional[str] = "It was not informed"):
        await self.handle_moderation_action(interaction, member, reason, action="mute", duration=duration)

    async def handle_moderation_action(self, interaction: discord.Interaction, member: discord.Member, reason: str, action: str, duration: Optional[int] = None):
        emoji = self.emojis_personalizados
        action_text = "ban" if action == "ban" else "kick" if action == "kick" else "mute"

        # Check if the author has the necessary permission or a special role
        has_permission = getattr(interaction.user.guild_permissions, f"{action}_members", None) or interaction.user.guild_permissions.manage_roles

        if not has_permission:
            # Check the database if there is a role that allows the action
            role_data = await self.bot.db.find_one("roles", {"guild_id": interaction.guild.id, f"{action}_permission": True})
            if role_data:
                role = interaction.guild.get_role(role_data["role_id"])
                if role in interaction.user.roles:
                    has_permission = True

        if not has_permission:
            await interaction.response.send_message(f"{emoji['raiva']} You do not have permission to {action_text} members.", ephemeral=True)
            return

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                f'{emoji["fazeoq"]} I cannot {action_text} the member <@{member.id}> because they are not below you.', ephemeral=True)
            return

        # Fetch the log channel from the "channels" collection in the database
        channel_data = await self.bot.db.find_one("channels", {"guild_id": interaction.guild.id, "name": "logban"})
        log_channel_id = channel_data.get("channel_id") if channel_data else None

        # If the log channel isn't set, prompt the user to set it
        if not log_channel_id:
            await interaction.response.send_message(
                f'{emoji["raiva"]} The log channel is not set. Please set a log channel first.', ephemeral=True)
            return

        log_channel = interaction.guild.get_channel(log_channel_id)
        if not log_channel:
            await interaction.response.send_message(
                f'{emoji["raiva"]} The configured log channel could not be found. Please check the settings.', ephemeral=True)
            return

        # Proceed with the moderation action
        await interaction.response.send_message(
            f'{emoji["pisca"]} **|** <@{interaction.user.id}>, You are about to {action_text} the member <@{member.id}>. To confirm this action, click the button below.',
            view=ModerationConfirmationView(member, reason, action, self.bot, log_channel, interaction.user, duration)
        )
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("mod")


class ModerationConfirmationView(discord.ui.View):
    ban_actions = defaultdict(list)  # Track ban actions per user

    def __init__(self, member, reason, action, bot, log_channel, interaction_user, duration=None):
        super().__init__()
        with open('data/db/emojispersonalizados.json', 'rb') as j:
            self.emojis_personalizados = json.load(j)
        with open('data/db/emojisdefault.json', 'rb') as j:
            self.emojis_padrao = json.load(j)
        self.member = member
        self.reason = reason
        self.action = action  # 'ban', 'kick', or 'mute'
        self.bot = bot
        self.log_channel = log_channel
        self.interaction_user = interaction_user  # The user who initiated the action
        self.duration = duration  # duration in minutes

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the user who clicked the button is the same as the user who initiated the action
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("You are not authorized to perform this action.", ephemeral=True)
            return

        # Check if the user is currently restricted from banning
        restricted_user = await self.bot.db.find_one("ban_restrictions", {"user_id": interaction.user.id, "guild_id": interaction.guild.id})
        if restricted_user:
            await interaction.response.send_message("You are temporarily restricted from banning members.", ephemeral=True)
            return

        if self.action == "ban":
            # Rate limit check: ensure the user hasn't banned more than 5 people in the last 2 minutes
            now = time.time()
            ModerationConfirmationView.ban_actions[interaction.user.id] = [
                timestamp for timestamp in ModerationConfirmationView.ban_actions[interaction.user.id] if now - timestamp < 120]  # 2 minutes

            if len(ModerationConfirmationView.ban_actions[interaction.user.id]) >= 5:
                # Temporarily revoke ban permissions for this specific user for 5 hours
                await self.revoke_ban_permission(interaction)

                # Log the action
                await self.log_channel.send(f"{interaction.user.mention} has been temporarily restricted from banning members for exceeding the ban limit.")
                await interaction.response.send_message(f"Your ability to ban members has been temporarily revoked due to exceeding the limit. You can ban again after 5 hours.", ephemeral=True)
                return

            # Register the current ban action
            ModerationConfirmationView.ban_actions[interaction.user.id].append(now)

            try:
                # Execute the ban
                await self.member.ban(reason=self.reason)
                if self.duration:
                    unban_time = datetime.now(timezone.utc) + timedelta(minutes=self.duration)
                    await self.bot.db.insert_one("bans", {"user_id": self.member.id, "guild_id": interaction.guild.id, "unban_time": unban_time})
                    self.bot.loop.create_task(self.schedule_unban(self.member, unban_time))

                await interaction.response.send_message(f'🔸 **|** The user was banned for: `{self.reason}`', ephemeral=True)

                # Log the ban
                embed = discord.Embed(
                    title=f"{self.bot.emojis_personalizados['coracao']} User Banned",
                    description=(
                        f'\n\n{self.bot.emojis_personalizados["coroa"]} **Author: {interaction.user.mention}**\n'
                        f'💎 **User:** {self.member.mention}\n'
                        f'🐉 **Reason:** {self.reason}'),
                    colour=8393472,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.set_thumbnail(url=self.member.display_avatar.url)
                await self.log_channel.send(embed=embed)

            except Exception as e:
                await interaction.response.send_message(f"An error occurred while trying to ban the user: {str(e)}", ephemeral=True)

    async def revoke_ban_permission(self, interaction):
        # Store the user restriction in the database for 5 hours
        await self.bot.db.insert_one(
            "ban_restrictions",
            {"user_id": interaction.user.id, "guild_id": interaction.guild.id, "restriction_end_time": datetime.now(timezone.utc) + timedelta(hours=5)}
        )

        # Schedule the lifting of the ban restriction after 5 hours
        self.bot.loop.create_task(self.lift_ban_restriction(interaction.user, interaction.guild, 5 * 3600))  # 5 hours in seconds

    async def lift_ban_restriction(self, user, guild, delay):
        await asyncio.sleep(delay)
        await self.bot.db.delete_one("ban_restrictions", {"user_id": user.id, "guild_id": guild.id})

    async def schedule_unban(self, member, unban_time):
        await discord.utils.sleep_until(unban_time)
        try:
            await member.guild.unban(member)
            await self.bot.db.delete_one("bans", {"user_id": member.id, "guild_id": member.guild.id})
        except Exception as e:
            print(f"Failed to unban {member}: {e}")

    async def schedule_unmute(self, member, mute_role, unmute_time):
        await discord.utils.sleep_until(unmute_time)
        try:
            await member.remove_roles(mute_role)
            await self.bot.db.delete_one("mutes", {"user_id": member.id, "guild_id": member.guild.id})
        except Exception as e:
            print(f"Failed to unmute {member}: {e}")

async def setup(bot):
    await bot.add_cog(Mod(bot))
