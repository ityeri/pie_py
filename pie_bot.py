import traceback
from typing import TYPE_CHECKING

from typing_extensions import override

from common_module.path_manager import get_data_folder

from common_module.admin_manager import *

from _commands import _commands

import os
import nextcord.ext
from nextcord.ext import commands
from nextcord.ext.commands import Context, errors


class PieBot(commands.Bot):

    def __init__(self):
        intents = nextcord.Intents.all()
        super().__init__(intents=intents)

        self.admin_manager: AdminManager | None = None

    def set_admin_manager(self, admin_manager: 'AdminManager'): self.admin_manager = admin_manager

    def init_folder(self):

        if not (os.path.exists("src/") and os.path.isdir("src/")):
            os.mkdir("src/")
        os.chdir("src/")

        if not (os.path.exists("data/") and os.path.isdir("data/")):
            os.mkdir("data/")

    def load_commands(self):
        for command_path in _commands:
            print(f" |  {command_path} 등록중...")
            # 혹시 익스텐션 로드 하는데 에러났니? _command.py 파일에 콤마 잘 넣었는지 봐봐
            self.load_extension(f"commands.{command_path}")

            print(f" |  {command_path} 등록 완료!")

    def start_bot(self, token: str):

        print("명령어 로딩중...")
        self.load_commands()
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
        self.admin_manager.load(self, get_data_folder("admins"))
        print("관리자 정보 로딩 완료")

        print('\nTimings Reset\n')


    @override
    async def on_command_error(self, context: Context, exception: errors.CommandError) -> None:
        print("===")
        print(f"{context.command} 의 실행중 에러가 발생했습니다!")
        print("===\n")

        traceback.print_exception(type(exception), exception, exception.__traceback__)
        print("")