import asyncio
import platform
import sys

import nextcord
from nextcord.ext import commands

try:
    from _token import TOKEN
except ModuleNotFoundError:
    raise ModuleNotFoundError("봇의 토큰이 저장되는 _token.py 파일을 찾을수 없습니다.")

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



intents = nextcord.Intents.all()
intents.message_content = True

bot: commands.Bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print("명령어를 동기화 합니다...")
    await bot.sync_application_commands()
    print("명령어 동기화 완료!\n")

    sys.exit(0)


print("\n봇을 키는중...")
bot.run(TOKEN)
