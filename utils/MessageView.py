import asyncio
import uuid
from typing import Optional, Callable, Any, Dict, List, Union
from discord import Message, Interaction, TextChannel
from pyee.asyncio import AsyncIOEventEmitter
from shared.types import ExtendedClient, MessageViewUpdate


class MessageView(AsyncIOEventEmitter):
    def __init__(
        self,
        message: Message,
        channel: TextChannel,
        client: ExtendedClient,
        filter_func: Optional[Callable[[Interaction], bool]] = None,
        timeout: Optional[int] = 60000,
    ):
        """
        MessageView is a utility for managing interactive views tied to messages in a Discord bot.
        """
        super().__init__()
        self.message = message
        self.channel = channel
        self.client = client
        self.msg_id = message.id
        self.filter_func = filter_func or (lambda _: True)
        self.timeout = timeout
        self.view_id = str(uuid.uuid4())
        self._timeout_task: Optional[asyncio.Task] = None

        # Register event listeners
        self.client.on("interaction_create", self._handle_interaction)
        self.client.on("message_delete", self._handle_message_delete)

        # Start timeout task if needed
        if self.timeout > 0:
            self._start_timeout()

    def _start_timeout(self):
        if self._timeout_task:
            self._timeout_task.cancel()
        self._timeout_task = asyncio.create_task(self._timeout_handler())

    async def _timeout_handler(self):
        await asyncio.sleep(self.timeout / 1000)
        self.destroy("timeout")

    async def _handle_interaction(self, interaction: Interaction):
        if interaction.message and interaction.message.id == self.msg_id:
            split_id = interaction.custom_id.split("-")
            event_id = split_id.pop(0)
            view_id = split_id.pop(-1)

            if view_id == self.view_id and self.filter_func(interaction):
                self.emit(event_id, interaction)
                self.emit("any", interaction)

    async def _handle_message_delete(self, message: Message):
        if message.id == self.msg_id:
            self.destroy("deleted")

    async def update(self, view: MessageViewUpdate) -> bool:
        """
        Update the view with new content, embeds, or components.
        """
        try:
            if "components" in view:
                view["components"] = self._add_random_id_to_buttons(view["components"])
            await self.message.edit(**view)
            return True
        except Exception as e:
            self.client.logger.error(f"Failed to update message view: {e}")
            return False

    def clone(self) -> "MessageView":
        """
        Create a cloned instance of this MessageView.
        """
        return MessageView(
            message=self.message,
            channel=self.channel,
            client=self.client,
            filter_func=self.filter_func,
            timeout=self.timeout,
        )

    def destroy(self, reason: Optional[str] = None):
        """
        Destroy this view and clean up listeners.
        """
        if self._timeout_task:
            self._timeout_task.cancel()
            self._timeout_task = None

        self.emit("end", reason or "destroy")
        self.remove_all_listeners()

        self.client.off("interaction_create", self._handle_interaction)
        self.client.off("message_delete", self._handle_message_delete)

    def _add_random_id_to_buttons(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adds a random ID to buttons for unique identification.
        """
        for row in rows:
            for component in row.get("components", []):
                custom_id = component.get("custom_id", "")
                split_id = custom_id.split("-")
                if split_id[-1] != self.view_id:
                    component["custom_id"] = f"{custom_id}-{self.view_id}"
        return rows


async def create_view(
    channel: TextChannel, client: ExtendedClient, view: MessageViewUpdate, filter_func: Optional[Callable[[Interaction], bool]] = None
) -> MessageView:
    """
    Create a MessageView tied to a newly sent message.
    """
    message = await channel.send(**view)
    return MessageView(message, channel, client, filter_func)


async def create_view_from_interaction(
    interaction: Interaction, client: ExtendedClient, view: MessageViewUpdate, filter_func: Optional[Callable[[Interaction], bool]] = None
) -> MessageView:
    """
    Create a MessageView tied to an interaction's response.
    """
    if not interaction.channel:
        raise ValueError("Interaction channel not found")

    response_message = await interaction.response.send_message(**view)
    return MessageView(response_message, interaction.channel, client, filter_func)


async def create_view_from_message(
    message: Message, client: ExtendedClient, filter_func: Optional[Callable[[Interaction], bool]] = None
) -> MessageView:
    """
    Create a MessageView tied to an existing message.
    """
    return MessageView(message, message.channel, client, filter_func)
