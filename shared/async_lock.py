import asyncio

class AsyncLock:
    """
    A custom asynchronous lock implementation using asyncio.Lock.
    """

    def __init__(self):
        self._lock = asyncio.Lock()

    async def acquire(self):
        """
        Acquires the lock asynchronously.
        """
        await self._lock.acquire()

    def release(self):
        """
        Releases the lock if it is currently held.
        """
        if self._lock.locked():
            self._lock.release()

    def is_locked(self):
        """
        Checks if the lock is currently held.
        """
        return self._lock.locked()

    async def __aenter__(self):
        """
        Acquires the lock when entering an asynchronous context.
        """
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Releases the lock when exiting an asynchronous context.
        """
        self.release()
