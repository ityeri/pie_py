import asyncio
import os

import discord
import dotenv
import logging

from extensions import extensions
from setup import bot, setup, log_handler, cli_runner


@bot.event
async def on_ready():
    logging.info(f'"{bot.user}" 로 로그인 완료')

    for ext in extensions:
        logging.info(f'익스텐션 "{ext}" 등록중')
        await bot.load_extension(ext)

    logging.info("Done!")
    logging.info("Timings Reset")

    loop = asyncio.get_running_loop()
    loop.create_task(cli_runner.run())

    logging.info("명령어 동기화중...")
    await bot.tree.sync()
    logging.info("명령어 동기화 완료")


if __name__ == "__main__":
    dotenv.load_dotenv(".env")

    setup()
    logging.info("봇을 시작합니다")
    logging.info("심심하다야")

    bot.run(
        os.getenv("BOT_TOKEN"),
        log_handler=log_handler,
        log_level=logging.INFO,
        root_logger=True
    )