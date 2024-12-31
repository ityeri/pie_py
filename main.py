import nextcord
import nextcord.context_managers
from nextcord.ext import commands
import os
import threading

from _token import TOKEN
from _commands import _commands
import nextcord.ext



class PieBot(commands.Bot):

    def __init__(self, intents):
        super().__init__(intents=intents)


    def initFolder(self):

        if not (os.path.exists("src/") and os.path.isdir("src/")):
            os.mkdir("src/")
        os.chdir("src/")

        if not (os.path.exists("data/") and os.path.isdir("data/")):
            os.mkdir("data/")


    def loadCommands(self):
        for commandPath in _commands:
            self.load_extension(f"commands.{commandPath}")

            print(f"{commandPath} 등록 완료!")


    async def on_ready(self):
        print("\n================")
        print(f'봇 "{self.user}" 에 연결했습니다!')
        print("================\n")

        print("명령어를 동기화 합니다...")
        await self.sync_application_commands()
        print("명령어 동기화 완료!\n")

        print('\nTimings Reset\n')



intents = nextcord.Intents.all()
intents.message_content = True

bot: PieBot = PieBot(intents)
bot.initFolder()
bot.loadCommands()


print("\n봇을 키는중...")
bot.run(TOKEN)