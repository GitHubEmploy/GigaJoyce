from typing import List, Optional, Callable, Dict, Any, Union
from discord import ButtonStyle, Interaction
from discord.ui import Button, View
from pyee.asyncio import AsyncIOEventEmitter

# Define os tipos AnyView e Page
AnyView = Union["MessageView", "InteractionView"]  # Tipos fictícios para serem definidos
Page = Dict[str, Any]  # Equivalente ao BaseMessageOptions no TS

# Enum para as flags do Paginator
class PaginatorFlags:
    WRAP = 1 << 0
    AUTO_INIT = 1 << 1

# Tipo para a função de atualização de página
PageUpdateFn = Callable[[Page], Page]

# Estilo de controle personalizado
ControlStyle = Dict[str, Optional[Button]]

class PaginatorComponent(AsyncIOEventEmitter):
    def __init__(
        self,
        view: AnyView,
        pages: List[Page],
        flags: Optional[List[int]] = None,
        page_update: Optional[PageUpdateFn] = None,
        control_style: Optional[ControlStyle] = None,
    ):
        super().__init__()
        self.view = view
        self.pages = pages
        self.flags = flags or [PaginatorFlags.WRAP]
        self.page_update = page_update
        self.current_page = 0
        self.total_pages = len(pages)

        # Configurar botões traduzidos
        self.buttons = self._setup_translated_buttons(control_style)

        # Configurar eventos de interação
        self.view.on("nextPage", self.next_page_interaction)
        self.view.on("previousPage", self.previous_page_interaction)

    def _setup_translated_buttons(self, control_style: Optional[ControlStyle]) -> Dict[str, Button]:
        """
        Configura os botões com traduções globais.
        """
        # Obter o idioma e as traduções
        client = self.view.client
        guild_id = self.view.interaction.guild.id if hasattr(self.view.interaction, "guild") else None
        language = client.translator.get_language_sync(guild_id) if guild_id else "en"
        translate = client.translator.get_global(language)

        # Configurar botões com rótulos traduzidos
        buttons = {
            "previous": Button(
                label=translate("paginator.previous"),
                style=ButtonStyle.primary,
                custom_id="previousPage",
            ),
            "select": Button(
                label=translate("paginator.select"),
                style=ButtonStyle.primary,
                custom_id="selectPage",
            ),
            "next": Button(
                label=translate("paginator.next"),
                style=ButtonStyle.primary,
                custom_id="nextPage",
            ),
        }

        # Substituir botões padrão por estilos personalizados, se fornecidos
        if control_style:
            buttons.update(control_style)

        return buttons



    def add_pagination_controls(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona controles de paginação ao layout da página.
        """
        if page_data.get("hasControls", False):
            return page_data

        # Adicionar botões diretamente como objetos Button
        row = View()
        row.add_item(self.buttons["previous"])
        row.add_item(self.buttons["select"])
        row.add_item(self.buttons["next"])

        # Adicionar o layout ao campo 'components'
        components = page_data.get("components", [])
        components.append(row)
        page_data["components"] = components
        page_data["hasControls"] = True

        return page_data


    async def update_view(self, page: int):
        """
        Atualiza a view com a página especificada.
        """
        page_data = self.page_update(self.pages[page]) if self.page_update else self.pages[page]
        page_data = self.add_pagination_controls(page_data)
        await self.view.update(page_data)

    async def next_page_interaction(self, interaction: Interaction):
        """
        Lida com a interação do botão "Próximo".
        """
        client = self.view.client
        guild_id = self.view.interaction.guild.id if hasattr(self.view.interaction, "guild") else None
        language = client.translator.get_language_sync(guild_id) if guild_id else "en"
        translate = client.translator.get_global(language)

        if self.current_page + 1 < self.total_pages:
            self.current_page += 1
            await interaction.response.defer_update()
            await self.update_view(self.current_page)
        elif PaginatorFlags.WRAP in self.flags:
            self.current_page = 0
            await interaction.response.defer_update()
            await self.update_view(self.current_page)
        else:
            await interaction.response.send_message(translate("paginator.last_page"), ephemeral=True)

    async def previous_page_interaction(self, interaction: Interaction):
        """
        Lida com a interação do botão "Anterior".
        """
        client = self.view.client
        guild_id = self.view.interaction.guild.id if hasattr(self.view.interaction, "guild") else None
        language = client.translator.get_language_sync(guild_id) if guild_id else "en"
        translate = client.translator.get_global(language)

        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.defer_update()
            await self.update_view(self.current_page)
        elif PaginatorFlags.WRAP in self.flags:
            self.current_page = self.total_pages - 1
            await interaction.response.defer_update()
            await self.update_view(self.current_page)
        else:
            await interaction.response.send_message(translate("paginator.first_page"), ephemeral=True)

    def set_update_function(self, fn: PageUpdateFn):
        """
        Define a função para atualizar as páginas.
        """
        self.page_update = fn

    async def next_page(self):
        """
        Avança para a próxima página programaticamente.
        """
        if self.current_page + 1 < self.total_pages:
            self.current_page += 1
            await self.update_view(self.current_page)

    async def previous_page(self):
        """
        Retorna à página anterior programaticamente.
        """
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_view(self.current_page)

    async def set_page(self, page: int):
        """
        Define uma página específica como a atual.
        """
        if 0 <= page < self.total_pages:
            self.current_page = page
            await self.update_view(self.current_page)

    async def init(self):
        """
        Inicializa o paginator na primeira página.
        """
        await self.update_view(self.current_page)
        self.view.refresh_timeout()


async def create_paginator(
    view: AnyView,
    pages: List[Page],
    flags: Optional[List[int]] = None,
    control_style: Optional[ControlStyle] = None,
) -> PaginatorComponent:
    """
    Cria e retorna um componente de paginação.
    """
    paginator = PaginatorComponent(view, pages, flags, None, control_style)
    if flags and PaginatorFlags.AUTO_INIT in flags:
        await paginator.init()
    return paginator
