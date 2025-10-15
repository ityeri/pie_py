from dataclasses import dataclass

from discord import Member


@dataclass
class CensorshipPolicy: # 예는 리턴용. 외부에서 생성해선 안되고 외부에서 받아서도 안됨
    policy_id: int
    guild: int
    content: str
    is_global: bool
    target_members: list[Member]