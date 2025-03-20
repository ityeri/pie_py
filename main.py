import asyncio
import platform

import nextcord

from pie_bot import PieBot
from common_module.admin_manager import AdminManager



OPUS_LOAD_PATH = "/opt/homebrew/opt/opus/lib/libopus.dylib"



try:
    from _token import TOKEN
except ModuleNotFoundError:
    raise ModuleNotFoundError("봇의 토큰이 저장되는 _token.py 파일을 찾을수 없습니다.")

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
elif platform.system() == "Darwin":
    # 다원 계열 운영체제 (macOS 등등) 일 경우, 오퍼스를 수동으로 로딩
    try:
        nextcord.opus.load_opus(OPUS_LOAD_PATH)
    except OSError:
        raise FileNotFoundError("Opus 의 경로가 잘못되었습니다.")


try:
    nextcord.opus.Encoder()
except:
    print("nextcord 내부의 Opus 관련 문제로 인해, 봇의 음성채팅 관련 기능이 작동하지 않습니다.")
    print("자세한 내용은"
          "https://github.com/Rapptz/discord.py/commit/bd637e2462697e32098efdaa314489631e215f20#diff-174d1d95f029b0a9ab22e0e7881eb3969aaecb92e6c3458687f71d93c8b7d34d"
          "를 참조해 주세요")


if __name__ == "__main__":
    pie_bot: PieBot = PieBot()

    pie_bot.init_folder()

    pie_bot.set_admin_manager(AdminManager())

    print("\n봇을 키는중...")
    pie_bot.start_bot(TOKEN)