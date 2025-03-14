from pie_bot import PieBot
from common_module.admin_manager import AdminManager

try:
    from _token import TOKEN
except ModuleNotFoundError:
    raise ModuleNotFoundError("봇의 토큰이 저장되는 _token.py 파일을 찾을수 없습니다.")


if __name__ == "__main__":
    pieBot: PieBot = PieBot()

    pieBot.set_admin_manager(AdminManager())

    print("\n봇을 키는중...")
    pieBot.start_bot(TOKEN)