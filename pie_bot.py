import traceback
from typing import TYPE_CHECKING

from typing_extensions import override

if TYPE_CHECKING:
    from common_module.admin_manager import *
from _commands import _commands

import os
import nextcord.ext
from nextcord.ext import commands
from nextcord.ext.commands import Context, errors


class PieBot(commands.Bot):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        intents = nextcord.Intents.all()
        super().__init__(intents=intents)

        self.adminManager: AdminManager | None = None

    def setAdminManager(self, adminManager: 'AdminManager'): self.adminManager = adminManager

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

            print(f" |  {commandPath} 등록 완료!")

    def startBot(self, token: str):

        print("명령어 로딩중...")
        self.loadCommands()
        print("명령어 로딩 완료!\n")

        print("봇에 연결합니다...")
        self.run(token)

    async def on_ready(self):
        print("===")
        print(f'봇 "{self.user}" 에 연결했습니다!')
        print("===\n")

        print("명령어를 동기화 합니다...")
        await self.sync_application_commands()
        print("명령어 동기화 완료!\n")

        print("관리자 정보 로드...")
        self.adminManager.load()
        print("관리자 정보 로딩 완료")

        print('\nTimings Reset\n')


    @override
    async def on_command_error(self, context: Context, exception: errors.CommandError) -> None:
        print("===")
        print(f"{context.command} 의 실행중 에러가 발생했습니다!")
        print("===\n")

        traceback.print_exception(type(exception), exception, exception.__traceback__)
        print("")