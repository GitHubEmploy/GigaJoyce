from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Optional, Union, TypeVar, Any, Generic, TYPE_CHECKING
from utils.InteractionView import InteractionView
from shared.types import ExtendedClient
from classes.structs.Guild import Guild
from classes.structs.Member import Member

if TYPE_CHECKING:
    from settings.DefaultTypes.boolean import BooleanSettingFile

T = TypeVar("T")


class Setting(ABC, Generic[T]):
    """
    Base class for all settings.
    """

    def __init__(
        self,
        name: str,
        description: str,
        id: str,
        type_: str,
        value: Optional[T] = None,
        permission: Optional[int] = None,
        locales: Optional[bool] = False,
        module_name: Optional[str] = None,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.id = id
        self.type = type_
        self.value = value
        self.permission = permission
        self.locales = locales
        self.module_name = module_name
        self.kwargs = kwargs


    def run(self, view: InteractionView) -> Awaitable[T]:
        """
        Executes the setting logic.
        This method must be implemented in derived classes.
        """
        raise NotImplementedError("Must be implemented in derived classes.")
        pass

    def parse_to_database(self, value: T) -> Any:
        """
        Converts the value to a format suitable for database storage.
        This method must be implemented in derived classes.
        """
        raise NotImplementedError("Must be implemented in derived classes.")
        pass


    def parse_from_database(self, config: Any) -> T:
        """
        Reconstructs the value from the database format.
        This method must be implemented in derived classes.
        """
        raise NotImplementedError("Must be implemented in derived classes.")
        pass

    async def parse(self, config: Any, client: ExtendedClient, guild_data: Any, guild: Guild) -> Awaitable[T]:
        """
        Parses the configuration data from the database or input.
        This method must be implemented in derived classes.
        """
        return config

    # def parse_to_field(self, value: T) -> str:
    #     """
    #     Converts the value into a human-readable string for display purposes.
    #     This method must be implemented in derived classes.
    #     """
    #     raise NotImplementedError("Must be implemented in derived classes.")
    #     pass

    def save(self, client: ExtendedClient, entity: Union["Guild", "Member"], setting: "Setting[T]") -> Awaitable[bool]:
        """
        Default method to save the value of a setting. This method can be overridden in derived classes.
        """
        client.logger.debug(f"Using default save method for setting: {self.id}")

        if hasattr(setting, "parse_to_database") and callable(setting.parse_to_database):
            value = setting.parse_to_database(setting.value)
        else:
            client.logger.warning(f"Setting does not have a parse_to_database method. Using raw value.")
            value = setting.value

        query = {f"settings.{setting.id}": value}

        if isinstance(entity, Guild):
            return client.db.update_one(
                "guilds",
                {"_id": str(entity.id)},
                {"$set": query},
            )
        elif isinstance(entity, Member):
            return client.db.update_one(
                "members",
                {"_id": str(entity.id)},
                {"$set": query},
            )
        else:
            raise TypeError("Entity must be a Guild or Member.")

    def apply_locale(self, translate_module: Callable[[str], str], clone: Optional[bool] = False) -> Union["Setting[T]", tuple[str, str, str]]:
        """
        Applies modular translation to all configurable fields.
        """
        if self.locales:
            if clone:
                setting_clone = self.clone()
                setting_clone.name = translate_module(self.name)
                setting_clone.description = translate_module(self.description)
                setting_clone.kwargs = {}
                for key, value in self.kwargs.items():
                    if isinstance(value, str):
                        setting_clone.kwargs[key] = translate_module(value)
                return setting_clone
            else:
                name = translate_module(self.name)
                description = translate_module(self.description)
                kwargs = {}
                for key, value in self.kwargs.items():
                    kwargs[key] = translate_module(value)
                return name, description, kwargs

    def propagate_locales(self, child: "Setting[Any]"):
        """
        Propagates `locales` and `module_name` to child settings.
        """
        if self.locales and self.module_name:
            child.locales = self.locales
            child.module_name = self.module_name

    def clone(self) -> "Setting[T]":
        """
        Returns a copy of the current setting instance.
        """
        cls = self.__class__
        init_params = cls.__init__.__code__.co_varnames[1:]  # Ignora 'self'
        init_args = {key: getattr(self, key) for key in init_params if hasattr(self, key)}
        return cls(**init_args)
