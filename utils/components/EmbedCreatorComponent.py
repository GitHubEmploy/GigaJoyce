import asyncio
import json
from typing import Callable, Optional, Union
from discord import Embed, Message, TextChannel, Interaction
from utils.MessageView import MessageView
from utils.InteractionView import InteractionView
from shared.types import MessageViewUpdate

# Definindo o tipo AnyView
AnyView = Union[MessageView, InteractionView]

# Constantes de tempo
SECOND = 1000  # Representa milissegundos

async def wait_for_user_input(
    view: AnyView,
    new_view: MessageViewUpdate,
    expiry: int,
    filter_func: Callable[[Message], bool],
    options: Optional[dict] = None,
) -> Union[str, None]:
    """
    Aguarda a entrada do usuário em uma mensagem ou interação.
    """
    options = options or {"deleteCollected": True}
    await view.update(new_view)
    channel: TextChannel = view.channel

    def check(message: Message):
        return filter_func(message)

    try:
        message = await view.client.wait_for(
            "message",
            check=check,
            timeout=expiry / SECOND,
        )

        if options.get("deleteCollected"):
            await message.delete()

        if message.content:
            return message.content

        if message.attachments:
            return message.attachments[0].url

    except asyncio.TimeoutError:
        return None


async def embed_creator(
    view: AnyView,
    filter_func: Callable[[Message], bool],
    should_complete: bool = True,
    data: Optional[Embed] = None,
) -> Embed:
    """
    Cria um embed interativo para ser configurado pelo usuário, com suporte a traduções globais.
    """
    client = view.client

    # Determinar o idioma
    guild_id = (
        view.interaction.guild.id if isinstance(view, InteractionView) and view.interaction.guild else
        view.message.guild.id if isinstance(view, MessageView) and view.message.guild else
        None
    )
    language = await client.translator.get_language(guild_id) if guild_id else "en"
    translate = client.translator.get_global(language)

    # Criar o embed padrão
    default_embed = Embed(
        title=translate("embed_creator.default_title"),
        description=translate("embed_creator.default_description"),
        color=0xFFFFFF,
    )
    embed = data or default_embed

    # Configurar os botões
    rows = [
        {"custom_id": "title", "label": translate("embed_creator.buttons.title")},
        {"custom_id": "description", "label": translate("embed_creator.buttons.description")},
        {"custom_id": "color", "label": translate("embed_creator.buttons.color")},
        {"custom_id": "image", "label": translate("embed_creator.buttons.image")},
        {"custom_id": "thumbnail", "label": translate("embed_creator.buttons.thumbnail")},
    ]

    await view.update(
        {
            "embeds": [embed.to_dict()],
            "components": [{"type": 1, "components": rows}],
        }
    )

    # Função para gerenciar eventos
    async def handle_event(event_name: str, prompt_key: str, update_func: Callable[[str], None]):
        question_embed = Embed(
            title=translate("embed_creator.editing"),
            description=translate(prompt_key),
            color=0xFFFFFF,
        )

        await view.update({"embeds": [question_embed.to_dict()], "components": []})
        user_input = await wait_for_user_input(view, {}, 30 * SECOND, filter_func)

        if user_input:
            update_func(user_input)
            await view.update(
                {"embeds": [embed.to_dict()], "components": [{"type": 1, "components": rows}]}
            )
        else:
            error_embed = Embed(
                title=translate("embed_creator.error"),
                description=translate("embed_creator.error_timeout"),
                color=0xFF0000,
            )
            await view.update({"embeds": [error_embed.to_dict()]})

    # Eventos
    async def on_title(_interaction):
        await handle_event(
            "title",
            "embed_creator.prompts.title",
            lambda input: embed.update(title=input),
        )

    async def on_description(_interaction):
        await handle_event(
            "description",
            "embed_creator.prompts.description",
            lambda input: embed.update(description=input),
        )

    # Registrar eventos no view
    view.on("title", on_title)
    view.on("description", on_description)

    if should_complete:
        view.on(
            "finish",
            lambda _interaction: asyncio.create_task(view.destroy("Finalizado")),
        )

    return embed
