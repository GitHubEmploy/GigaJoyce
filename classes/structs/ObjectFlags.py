from discord.ext.commands import Bot
from typing import Any, Dict
import logging


class ObjectFlags:
    """
    Manages custom flags for a Guild or User object.
    """

    def __init__(self, client: Bot, obj: Any):
        """
        Inicializa o gerenciador de flags para um objeto Guild ou Member.
        """
        self.client = client
        self.obj = obj  # Pode ser uma instância de Guild ou outra classe
        self.logger = logging.getLogger(f"{self.obj.id} Flags")  # Use o atributo id diretamente

    def set(self, flag: str, value: Any) -> bool:
        """
        Sets a custom flag.
        """
        if flag not in self.client.flags.flags:
            self.logger.warning(f"Flag '{flag}' is not registered, ignoring.")
            return False
        if not hasattr(self.obj, "data") or not isinstance(self.obj.data, dict):
            self.logger.error(f"Object '{self.obj}' does not have a valid data attribute.")
            return False
        self.obj.data.setdefault("flags", {})[flag] = value
        return True

    async def awaitable_set(self, flag: str, value: Any) -> bool:
        """
        Sets a custom flag asynchronously.
        """
        if flag not in self.client.flags.flags:
            self.logger.warning(f"Flag '{flag}' is not registered, ignoring.")
            return False
        if not hasattr(self.obj, "data") or not isinstance(self.obj.data, dict):
            self.logger.error(f"Object '{self.obj}' does not have a valid data attribute.")
            return False
        self.obj.data.setdefault("flags", {})[flag] = value
        return True

    def delete(self, flag: str) -> bool:
        """
        Deletes a custom flag.
        """
        if hasattr(self.obj, "data") and "flags" in self.obj.data:
            self.obj.data["flags"].pop(flag, None)
            return True
        return False

    def get(self, flag: str) -> Any:
        """
        Retrieves the value of a custom flag.
        """
        if hasattr(self.obj, "data") and "flags" in self.obj.data:
            return self.obj.data["flags"].get(flag, self.client.flags.flags.get(flag))
        return self.client.flags.flags.get(flag)

    def has(self, flag: str) -> bool:
        """
        Checks if a flag is set.
        """
        return flag in self.client.flags.flags

    @property
    def all(self) -> Dict[str, Any]:
        """
        Returns all flags.
        """
        if hasattr(self.obj, "data") and "flags" in self.obj.data:
            return self.obj.data["flags"]
        return {}
