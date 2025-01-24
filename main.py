from _token import TOKEN
from pie_bot import PieBot
from common_module.admin_manager import AdminManager

if __name__ == "__main__":
    pieBot: PieBot = PieBot()

    pieBot.setAdminManager(AdminManager())

    print("\n봇을 키는중...")
    pieBot.startBot(TOKEN)