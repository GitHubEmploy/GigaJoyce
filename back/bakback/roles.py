import discord
import json
from discord import app_commands
from discord.ext import commands
import time
from datetime import datetime, timezone
from PIL import Image, ImageDraw
import aiohttp
import io, os, json

class RoleMenu(discord.ui.Select):
    def __init__(self, roles, toggle):
        self.toggle = toggle
        options = [
            discord.SelectOption(label=role['name'], value=role['id'], emoji=role.get('emoji'))
            for role in roles
        ]
        super().__init__(placeholder="Select a Role", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])

        role = discord.utils.get(interaction.guild.roles, id=role_id)

        if role:
            if self.toggle:  # Lógica do "toggle role"
                for menu_role in self.options:
                    role_to_remove = discord.utils.get(interaction.guild.roles, id=int(menu_role.value))
                    if role_to_remove in interaction.user.roles:
                        await interaction.user.remove_roles(role_to_remove)

            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"Role {role.name} removed!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"Role {role.name} added!", ephemeral=True)

class RoleView(discord.ui.View):
    def __init__(self, roles, toggle, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(RoleMenu(roles, toggle))

class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_data_path = "data/db/emoji_data.json"  # Caminho do JSON onde as informações serão salvas
        self.load_emoji_data()

    def load_emoji_data(self):
        """Carrega os dados do JSON, se existirem."""
        if os.path.exists(self.emoji_data_path):
            with open(self.emoji_data_path, 'r') as f:
                self.emoji_cache = json.load(f)
        else:
            self.emoji_cache = {}

    def save_emoji_data(self):
        """Salva os dados dos emojis no JSON."""
        with open(self.emoji_data_path, 'w') as f:
            json.dump(self.emoji_cache, f, indent=4)

    def generate_circular_image(self, color, filename):
        """Gera uma imagem circular com a cor do cargo e salva a imagem."""
        img_size = 128
        image = Image.new("RGBA", (img_size, img_size), (255, 255, 255, 0))  # Transparente
        draw = ImageDraw.Draw(image)
        draw.ellipse((0, 0, img_size, img_size), fill=color)

        # Salva a imagem localmente
        image.save(filename)
        
    async def get_application_emojis(self):
        """Realiza uma request para obter os emojis da aplicação (App Emojis)."""
        app_info = await self.bot.application_info()
        app_id = app_info.id
        url = f"https://discord.com/api/v10/applications/{app_id}/emojis"
        
        headers = {
            "Authorization": f"Bot {self.bot.http.token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to fetch application emojis: {response.status}")
                    return []


    async def get_or_create_emoji_for_role(self, role, name, guild):
        """Verifica se o emoji para a cor já existe no App Emojis, caso contrário, cria um novo."""
        color_hex = role.color.value
        filename = f"emoji_{color_hex}.png"

        # Busca os emojis da aplicação (App Emojis)
        app_emojis = await self.get_application_emojis()

        # Verifica se o emoji já foi criado anteriormente
        for emoji in app_emojis["items"]:
            if emoji['name'] == f"{name.lower()}":
                return discord.PartialEmoji(id=emoji['id'], name=emoji['name'])

        if role.color.value != 0:  # Verifica se a role tem uma cor definida
            color_rgb = role.color.to_rgb()
            self.generate_circular_image(color_rgb, filename)

            # Lê a imagem gerada para criar o emoji
            with open(filename, 'rb') as image_file:
                image_data = image_file.read()

            try:
                emoji = await guild.create_custom_emoji(name=f"{name.lower()}_{color_hex}", image=image_data)

                self.emoji_cache[color_hex] = {"emoji_id": emoji.id, "image": filename}
                self.save_emoji_data()

                return emoji
            except discord.HTTPException as e:
                print(f"Error while creating emoji: {e}")
                return None

    @app_commands.command(name="createmenu")
    @app_commands.default_permissions(administrator=True)
    async def create_menu(self, interaction: discord.Interaction, title:str, content:str, timeout: int, toggle: bool, *, args: str):
        roles = []
        role_args = args.split(';')
        guild = interaction.guild
        await interaction.response.send_message(f"Configuring role...", ephemeral=True)
        for role_arg in role_args:
            details = role_arg.split(',')
            name = details[0].strip()
            role_id = int(details[1].strip())
            
            emoji = discord.utils.get(self.bot.emojis, name=name) if len(details) < 3 else details[2]
 
            # Busca o cargo pelo ID
            role = discord.utils.get(interaction.guild.roles, id=role_id)

            # Se o cargo tiver uma cor, cria ou busca o emoji no cache
            if not emoji and role:

                emoji = await self.get_or_create_emoji_for_role(role, name, guild)
            # print(emoji)
            # Convertendo o emoji para string (representação serializável)
            roles.append({"name": name, "id": role_id, "emoji": str(emoji) if emoji else None})


        if timeout == 0:
            timeout = None
        

        embed = discord.Embed(
            title=title,
            description=content,
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        # for role in roles:
        #     embed.add_field(name=role['name'], value=role['description'], inline=False)

        
        message = await interaction.followup.send(embed=embed, view=RoleView(roles, toggle, timeout=timeout))

        # Salva o menu no JSON com o ID da mensagem
        with open("data/db/menus.json", "r") as f:
            menus_data = json.load(f)

        menus_data[str(message.id)] = {
            "channel_id": interaction.channel_id,
            "roles": roles,
            "toggle": toggle,
            "timeout": timeout
        }

        with open("data/db/menus.json", "w") as f:
            json.dump(menus_data, f)

    @commands.Cog.listener()
    async def on_ready(self):
        # Restaurar menus na inicialização do bot
        with open("data/db/menus.json", "r") as f:
            menus_data = json.load(f)

        for message_id, data in menus_data.items():
            channel = self.bot.get_channel(int(data.get("channel_id")))
            try:
                message = await channel.fetch_message(int(message_id))
                roles = data["roles"]
                toggle = data["toggle"]
                timeout = data["timeout"]

                await message.edit(view=RoleView(roles, toggle, timeout=timeout))
            except discord.NotFound:
                print(f"Mensagem com ID {message_id} não encontrada. Ignorando.")
        
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("roles")

exports = [RoleCog]
