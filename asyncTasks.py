import asyncio
from nextcord.message import Message
from nextcord.interactions import Interaction



class AsyncTask:
    def __init__(self):
        self.on = False

    async def update(self) -> None: ...

    async def run(self, delay: float) -> None:
        self.on = True
        while self.on:
            await self.update()
            await asyncio.sleep(delay)

    def stop(self) -> None:
        self.on = False


class AsyncMessageTask(AsyncTask):
    def __init__(self, message: Message, interaction: Interaction):
        super().__init__()
        self.message: Message = message
        self.interaction: Interaction = interaction
    
    async def setMessage(self, content: str = None, **kargs):
        await self.message.edit(content, **kargs)