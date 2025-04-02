from typing import Optional, Callable, Dict, List, Any
from discord import Interaction, TextChannel, Message, Embed
from discord.ui import View, Button, Select
from discord.ext.commands import Bot
from shared.types import ExtendedClient
from pyee.asyncio import AsyncIOEventEmitter
import asyncio
import uuid


class InteractionView(View, AsyncIOEventEmitter):
    def __init__(
        self,
        interaction: Interaction,
        channel: TextChannel,
        client: ExtendedClient,
        ephemeral: Optional[bool] = False,
        filter_func: Optional[Callable[[Interaction], bool]] = None,
        timeout: Optional[int] = 60,  # Timeout em segundos
        parent: Optional["InteractionView"] = None,
    ):
        """
        InteractionView gerencia visualizações interativas para um bot Discord e emite eventos personalizados.

        :param interaction: A interação inicial que gerou a view.
        :param channel: O canal de texto onde a interação ocorreu.
        :param client: A instância do cliente do bot.
        :param ephemeral: Se a resposta deve ser efêmera.
        :param filter_func: Função para filtrar interações.
        :param timeout: Tempo limite para a view expirar.
        :param parent: Referência para a view pai, se for um clone.
        """
        # Inicializa as classes pai
        View.__init__(self, timeout=timeout)
        AsyncIOEventEmitter.__init__(self)

        self.interaction = interaction
        self.channel = channel
        self.client = client
        self.ephemeral = ephemeral
        self.filter_func = filter_func or (lambda i: True)
        self.parent = parent

        self.msg_id: Optional[str] = interaction.message.id if interaction.message else None
        self.view_id: str = self._generate_random_id()

        # Inicializa o atributo _timeout_task
        self._timeout_task: Optional[asyncio.Task] = None

        # Registra o listener para exclusão de mensagens
        self.client.add_listener(self._handle_message_delete, "on_message_delete")

        # Inicia o timeout da view
        if self.timeout is not None and self.timeout > 0:
            self.start_timeout()

        # Debugging logs
        self.client.logger.debug(f"InteractionView initialized with view_id: {self.view_id}, message ID: {self.msg_id}, ephemeral: {self.ephemeral}")

    @staticmethod
    def _generate_random_id() -> str:
        """
        Gera um ID aleatório único para a view.

        :return: ID único como string.
        """
        return str(uuid.uuid4())

    async def on_timeout(self):
        """
        Método chamado quando a view expira (timeout).
        Emite o evento 'end' com a razão 'timeout'.
        """
        self.client.logger.debug(f"View with view_id {self.view_id} has timed out.")
        self.emit("end", "timeout")
        self.destroy("timeout")

    async def _handle_message_delete(self, message: Message):
        """
        Método chamado quando uma mensagem é deletada.
        Emite o evento 'end' com a razão 'deleted' se a mensagem for a da view.

        :param message: Mensagem que foi deletada.
        """
        if message.id == self.msg_id:
            self.client.logger.debug(f"Message with ID {self.msg_id} was deleted, triggering view destruction.")
            self.emit("end", "deleted")
            self.destroy("deleted")

    def start_timeout(self):
        """
        Inicia ou reinicia o timeout da view.
        """
        if self._timeout_task:
            self._timeout_task.cancel()
        self.client.logger.debug(f"Starting timeout for view with view_id: {self.view_id}")
        self._timeout_task = asyncio.create_task(self._timeout_handler())

    async def _timeout_handler(self):
        """
        Handler para gerenciar o timeout da view.
        """
        await asyncio.sleep(self.timeout)
        await self.on_timeout()

    async def update(self, **kwargs) -> bool:
        """
        Atualiza a visualização com novos dados.

        :param kwargs: Dados para atualização, como embeds e a view associada.
        :return: True se a atualização for bem-sucedida, False caso contrário.
        """
        try:
            # Limpa os componentes existentes, se especificado
            components = kwargs.pop("components", [])
            self.client.logger.debug(f"Updating view with components: {components}")
            self.clear_items()
            for component in components:
                component = self._add_custom_id(component)
                self.add_item(component)

            # Atualiza ou envia uma mensagem dependendo do estado da interação
            if self.interaction.response.is_done():
                await self.interaction.edit_original_response(view=self, **kwargs)
            else:
                await self.interaction.response.send_message(view=self, **kwargs, ephemeral=self.ephemeral)
            self.client.logger.debug("View updated successfully.")
            return True
        except Exception as e:
            self.client.logger.error(f"Failed to update interaction view: {e}")
            return False

    def _add_custom_id(self, component: Any) -> Any:
        """
        Garante que o componente tenha o `view_id` anexado ao `custom_id`.
        """
        if hasattr(component, "custom_id") and component.custom_id:
            split_id = component.custom_id.split("-")
            if len(split_id) > 1 and "-".join(split_id[1:]) == self.view_id:
                return component 
            component.custom_id = f"{component.custom_id}-{self.view_id}"
            self.client.logger.debug(f"Updated custom_id for component: {component.custom_id} | View Id: {self.view_id}")
        return component
    
    def normalize_custom_id(self, custom_id: str) -> str:
        """
        Remove a parte da `view_id` anexada ao `custom_id`, se existir.
        """
        normalized_id = custom_id.split("-")[0] if "-" in custom_id else custom_id
        self.client.logger.debug(f"Normalized custom_id: {custom_id} -> {normalized_id}")
        return normalized_id
    
    def clone(self) -> "InteractionView":
        """
        Clona esta instância de InteractionView.

        :return: Nova instância de InteractionView clonada.
        """
        self.client.logger.debug(f"Cloning InteractionView with view_id: {self.view_id}")
        cloned_view = InteractionView(
            interaction=self.interaction,
            channel=self.channel,
            client=self.client,
            ephemeral=self.ephemeral,
            filter_func=self.filter_func,
            timeout=self.timeout,
            parent=self
        )
        cloned_view.set_msg_id(self.msg_id)
        return cloned_view

    def set_msg_id(self, msg_id: str):
        """
        Define o ID da mensagem associada à view.

        :param msg_id: ID da mensagem.
        """
        self.msg_id = msg_id
        self.client.logger.debug(f"Message ID set for view: {msg_id}")

    def destroy(self, reason: Optional[str] = None):
        """
        Destroi a view e limpa os listeners.

        :param reason: Razão para destruir a view.
        """
        if self._timeout_task:
            self._timeout_task.cancel()
            self._timeout_task = None

        # Remove a view do registro, se existir
        if self.client.view_registry and self.msg_id in self.client.view_registry:
            del self.client.view_registry[self.msg_id]

        self.emit("end", reason or "destroy")
        self.clear_items()  # Remove todos os componentes

        # Verifica se o evento foi registrado antes de tentar removê-lo
        if "on_message_delete" in self._events:
            self.client.remove_listener("on_message_delete", self._handle_message_delete)

        self.stop()  # Para o timeout da view
        self.client.logger.debug(f"InteractionView with view_id {self.view_id}, {reason}.")
    
    def set_extra_filter(self, filter_func: Callable[[Interaction], bool]):
        """
        Define uma função de filtro adicional para interações.

        :param filter_func: Função que recebe uma interação e retorna um booleano.
        """
        self.filter_func = filter_func
        self.client.logger.debug(f"Extra filter function set for InteractionView {self.view_id}")
