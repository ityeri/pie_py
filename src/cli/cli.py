import asyncio
from abc import ABC, abstractmethod
import logging

from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession


class CommandExecutor(ABC):
    command_name: str

    @abstractmethod
    async def on_command(self, args: list[str]) -> bool: ...


class CLIRunner:
    def __init__(self):
        self.executors: list[CommandExecutor] = list()
        self.logger = logging.getLogger("CLIRunner")

    def start(self):
        asyncio.create_task(self.run())

    async def run(self):
        session = PromptSession("> ")

        while True:
            with patch_stdout():
                command = await session.prompt_async()
            command_slices = command.split()

            if len(command_slices) <= 0: continue

            is_executed = False

            for executor in self.executors:
                if executor.command_name == command_slices[0]:
                    is_executed = True
                    try:
                        await executor.on_command(command_slices[1:len(command_slices)])
                    except Exception as e:
                        logging.error(f"\"{executor.command_name}\" 실행중 에러 발생: ")
                        logging.exception(e)

            if not is_executed:
                logging.error(f"명령어 \"{command_slices[0]}\" 을 찾을수 없습니다")

    def add_executor(self, executor: CommandExecutor):
        self.executors.append(executor)