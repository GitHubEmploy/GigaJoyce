# types.py

from typing import Callable, Awaitable, Dict, Union, Optional
from discord.ext.commands import Bot
from discord import GuildMember, TextChannel

# Definição de tipos para Permissão
PermissionNode = Callable[[Bot, str, GuildMember, TextChannel], Awaitable[bool]]
RecursiveMap = Dict[str, Union['RecursiveMap', PermissionNode]]
OverrideNode = Dict[str, list]  # {'allow': [permissions], 'deny': [permissions]}
