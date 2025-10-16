from dataclasses import dataclass

from discord import Member, Guild


@dataclass
class CensorshipPolicy: # 예는 리턴용. 외부에서 생성해선 안되고 외부에서 받아서도 안됨
    guild: Guild
    content: str
    is_global: bool
    target_members: list[Member] | None