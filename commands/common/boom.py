import nextcord
from nextcord.ext import commands
from commonModule.async_tasks import AsyncMessageTask

class status:
    WAIT = 0
    COUTING = 1
    DEL_WAIT = 2

class BoomTask(AsyncMessageTask):
    def __init__(self, message, interaction):
        super().__init__(message, interaction)
        self.status = 0
        self.count = 0
    
    async def update(self):
        if self.status == status.WAIT:
            self.status = status.COUTING
            self.count = 5
            await self.setMessage(f"자폭까지 {self.count}초 남음..")
        
        elif self.status == status.COUTING:
            self.count -= 1

            if self.count != 0:
                await self.setMessage(f"자폭까지 {self.count}초 남음..")
            
            else:
                with open("boom.gif", "rb") as gif_file:
                    gif = nextcord.File(gif_file, filename="boom.gif")
                    await self.setMessage(file=gif)
                
                await self.message.delete(delay=10)

                self.stop()


class Boom(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(name='자폭', description="안터짐")
    async def boom(self, interaction: nextcord.Interaction):
        message = await interaction.send("설마 터지겠어")
        await BoomTask(message, interaction).run(1)


def setup(bot: commands.Bot):
    bot.add_cog(Boom(bot))