import os
import dotenv
import discord
from discord.ext import commands
import logging

from extensions import extensions


log_handler = logging.FileHandler(filename='latest.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    logging.info(f'"{bot.user}" 로 로그인 완료')

    for ext in extensions:
        logging.info(f'익스텐션 "{ext}" 등록중')
        await bot.load_extension(ext)

    logging.info("Done!")
    logging.info("Timings Reset")

    logging.info("명령어 동기화중...")
    await bot.tree.sync()
    logging.info("명령어 동기화 완료")


if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    discord.utils.setup_logging()

    logging.info("봇을 시작합니다")

    bot.run(
        os.getenv("BOT_TOKEN"),
        log_handler=log_handler,
        log_level=logging.INFO,
        root_logger=True
    )