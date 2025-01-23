import nextcord
from nextcord.ext import commands
from _token import TOKEN
import asyncio
import sys

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
