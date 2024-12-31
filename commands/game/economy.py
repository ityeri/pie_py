import nextcord
from nextcord.ext import commands
# pppppppppㅔㅔㅔㅔㅔㅔㅔㅔ 플로트 오차 조까라그랰ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ


class Loan:
    def __init__(self, bankbook: 'UserBankbook'):
        self.amount: int
        self.interestRate: float
        self.bankbook: UserBankbook = UserBankbook

    def loan(self, amount: int): self.amount += amount
    
    def repayment(self, amount: int):
        ...
    
    def chargeInterest(self):
        self.bankbook.asset -= self.amount * (self.interestRate / 100)

class UserBankbook:
    def __init__(self, user: nextcord.User):
        self.user: nextcord.User = user

        # 신용 점수는 0 ~ 1000 까지
        self.creditScore: int = 620
        # 자산은 음수도 가능ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ
        self.asset: float = 0.0
    
    def loan(self, value: int): ... # 0.25 (1등급)