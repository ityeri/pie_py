import nextcord
import nextcord.context_managers
from nextcord.ext import commands
import os
import threading

from _token import TOKEN
from _commands import _commands
import nextcord.ext

from tqdm import tqdm

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(intents=intents)

def commandlineHandling():
    while True:
        command = input("_> ")
        onCommand(command)

def onCommand(command: str):
    try:
        commandWords = command.split(' ')
        if commandWords[0] == 'reload':
            bot.reload_extension(f"commands.{commandWords[1]}")
        elif commandWords[0] == 'load':
            bot.load_extension(f"commands.{commandWords[1]}")
            
    except:
        print("명령어 똑바로좀 쳐봐")



@bot.event
async def on_ready():
    print("\n================")
    print(f'봇 "{bot.user}" 에 연결했습니다!')
    print("================\n")
    print("명령어를 동기화 합니다...")
    await bot.sync_application_commands()
    print("명령어 동기화 완료!\n")

    print('\nTimings Reset\n')

    commandlineThread = threading.Thread(target=commandlineHandling, daemon=True)
    commandlineThread.start()

os.chdir("src/")

for commandPath in _commands:
    bot.load_extension(f"commands.{commandPath}")
    print(f"{commandPath} 등록 완료!")

print("\n봇을 키는중...")
bot.run(TOKEN)