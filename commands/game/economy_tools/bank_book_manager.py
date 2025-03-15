from typing import Any

from nextcord import User
from nextcord.ext.commands import Bot

from .stocks_preset import StocksManager
from .user_bank_book import UserBankbook


class BankBookManager:

    def __init__(self):
        self.user_bank_books: dict[User, UserBankbook] = dict()

    def get_bank_book(self, user: User, auto_gen: bool=True) -> UserBankbook:
        if user not in self.user_bank_books and auto_gen:
            self.user_bank_books[user] = UserBankbook(user, 1000_0000)
        return self.user_bank_books[user]



    @classmethod
    def from_json(cls, data: dict[int, dict], bot: Bot, stock_manager: StocksManager) -> 'BankBookManager':
        bank_book_manager = BankBookManager()
        for user_id, bank_book_data in data:
            bank_book_manager.user_bank_books[bot.get_user(user_id)] = (
                UserBankbook.from_json(bank_book_data, bot, stock_manager))

        return bank_book_manager

    def to_json(self) -> dict[int, dict]:
        return {user.id: bank_book.to_json() for user, bank_book in self.user_bank_books.items()}