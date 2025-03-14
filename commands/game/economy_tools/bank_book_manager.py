from nextcord import User

from .user_bank_book import UserBankbook


class BankBookManager:

    def __init__(self):
        self.user_bank_books: dict[User, UserBankbook] = dict()

    def get_bank_book(self, user: User, auto_gen: bool=True) -> UserBankbook:
        if user not in self.user_bank_books and auto_gen:
            self.user_bank_books[user] = UserBankbook(user, 1000_0000)
        return self.user_bank_books[user]