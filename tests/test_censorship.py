import logging
import os

import dotenv

from pie_py.setup import bot, setup, log_handler
from pie_py.censorship.core.censorship_manager import CensorshipManager

guild1 = bot.get_guild(967763148285308938)
guild2 = bot.get_guild(1052159030212173904)
user1 = bot.get_user(1245271388282028034)
user2 = bot.get_user(889963585797771305)

@bot.event
async def on_ready():
    global guild1, guild2, user1, user2

    guild1 = bot.get_guild(967763148285308938)
    guild2 = bot.get_guild(1052159030212173904)
    user1 = bot.get_user(1245271388282028034)
    user2 = bot.get_user(889963585797771305)

    # generate_test_data()

    # CensorshipManager.rm_policy(guild1, 'asdf')
    # CensorshipManager.rm_policy(guild1, 'qwer') # must be error

    # CensorshipManager.rm_policy(guild2, 'qwer')
    # CensorshipManager.rm_policy(guild2, 'asdf') # must be error

    # CensorshipManager.rm_member_policy(guild1, user1, 'qwer')

    await bot.close()

def generate_test_data():
    CensorshipManager.add_policy(guild1, 'asdf', is_global=True)
    CensorshipManager.add_policy(guild2, 'qwer', is_global=False)
    CensorshipManager.add_member_policy(guild1, user1, 'asdf')
    CensorshipManager.add_member_policy(guild2, user2, 'qwer')

if __name__ == "__main__":
    dotenv.load_dotenv()

    setup()
    logging.info("봇을 시작합니다")
    logging.info("심심하다야")

    bot.run(
        os.getenv("BOT_TOKEN"),
        log_handler=log_handler,
        log_level=logging.INFO,
        root_logger=True
    )