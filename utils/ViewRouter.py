import asyncio
from typing import Any, Dict, List, Optional, Union
from pyee.asyncio import AsyncIOEventEmitter
from uuid import uuid4
from discord import ActionRow


class ViewRouter(AsyncIOEventEmitter):
    """A class to manage a navigation stack for interactive views."""

    def __init__(self, logger, view):
        """
        Initialize the ViewRouter.

        Args:
            logger: Logger instance for logging.
            view: The current active view (e.g., InteractionView or similar).
        """
        super().__init__()
        self.logger = logger.getChild("ViewRouter")
        self.stack: List[Dict[str, Any]] = []
        self.view = view
        self.forced_rows: List[ActionRow] = []

        # Forward events from the managed view to this router
        self._forward_events(view, self)

        # Handle "returnPage" event to pop the view
        self.on("returnPage", self.pop)

    def _forward_events(self, forwarder, forwarded):
        """Forward events from one EventEmitter to another."""
        original_emit = forwarder.emit

        def new_emit(event_name: str, *args):
            forwarded.emit(event_name, *args)
            return original_emit(event_name, *args)

        forwarder.emit = new_emit

    def set_view(self, view):
        """Set the active view managed by the router."""
        self.view = view

    def set_rows(self, rows: List[ActionRow]):
        """Set persistent rows to append to every page."""
        self.forced_rows = rows

    async def push(self, update: Dict[str, Any]) -> str:
        """
        Push a new page onto the navigation stack.

        Args:
            update: A dictionary containing the new view's content and components.

        Returns:
            A unique ID for the pushed page.
        """
        page_id = str(uuid4())
        self.stack.append({"style": update, "id": page_id})

        # Append forced rows to components
        if "components" in update:
            update["components"] += self.forced_rows
        else:
            update["components"] = self.forced_rows

        await self.view.update(update)
        return page_id

    async def pop(self):
        """
        Pop the current page from the navigation stack.

        Returns:
            The unique ID of the popped page, or None if the stack is empty.
        """
        if not self.stack:
            return None

        page = self.stack.pop()
        await self.view.update(page["style"])
        return page["id"]

    def clear_stack(self):
        """Clear the navigation stack."""
        self.stack = []

    async def update(self, update: Dict[str, Any]) -> bool:
        """
        Update the current view without modifying the stack.

        Args:
            update: A dictionary containing the updated view's content and components.

        Returns:
            True if the update was successful, False otherwise.
        """
        return await self.view.update(update)

    async def destroy(self):
        """Destroy the view and clean up resources."""
        await self.view.destroy()
