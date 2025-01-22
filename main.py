import os

import nextcord.ext

from _commands import _commands
from _token import TOKEN
from common_module.admin_manager import *


class PieBot(commands.Bot):

    def __init__(self, intents):
        super().__init__(intents=intents)
        self.adminManager: AdminManager = AdminManager()


    def initFolder(self):

        if not (os.path.exists("src/") and os.path.isdir("src/")):
            os.mkdir("src/")
        os.chdir("src/")

        if not (os.path.exists("data/") and os.path.isdir("data/")):
            os.mkdir("data/")


    def loadCommands(self):
        for commandPath in _commands:

            # 혹시 익스텐션 로드 하는데 에러났니? _command.py 파일에 콤마 잘 넣었는지 봐봐
            self.load_extension(f"commands.{commandPath}")

            print(f"{commandPath} 등록 완료!")


    async def on_ready(self):
        print("\n================")
        print(f'봇 "{self.user}" 에 연결했습니다!')
        print("================\n")

        print("명령어를 동기화 합니다...")
        await self.sync_application_commands()
        print("명령어 동기화 완료!\n")

        self.adminManager.load(self)

        print('\nTimings Reset\n')


if __name__ == "__main__":
    intents = nextcord.Intents.all()
    intents.message_content = True

    bot: PieBot = PieBot(intents)
    bot.initFolder()
    bot.loadCommands()


    print("\n봇을 키는중...")
    bot.run(TOKEN)