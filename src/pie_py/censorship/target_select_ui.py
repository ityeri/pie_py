from __future__ import annotations

from enum import Enum
from typing import Any

import discord.ui
from discord import Guild, Interaction, InteractionResponse

from pie_py.censorship.core.censorship import CensorshipManager
from pie_py.censorship.core.censorship.exceptions import PolicyNotFoundError


class LabeledTarget(Enum):
    ALL = ('서버의 모든 인원',)
    ONLY_CERTAIN_MEMBERS = ('지정된 특정 맴버만',)

    def __init__(self, label: str):
        self.label: str = label

    @classmethod
    def get_target_by_label(cls, label: str) -> LabeledTarget | None:
        for target in LabeledTarget:
            if target.label == label:
                return target
        return None


class TargetSelect(discord.ui.Select):
    def __init__(self, guild: Guild, content: str):
        self.guild: Guild = guild
        self.content: str = content

        options = [
            discord.SelectOption(label=LabeledTarget.ALL.label),
            discord.SelectOption(label=LabeledTarget.ONLY_CERTAIN_MEMBERS.label)
        ]

        super().__init__(
            placeholder='검열이 적용될 d대상 선택',
            min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: Interaction):
        target = LabeledTarget.get_target_by_label(self.values[0])
        res: InteractionResponse = interaction.response

        try:
            if target == LabeledTarget.ALL:
                CensorshipManager.set_global(self.guild, self.content, True)
                await res.send_message(f'이제 "{self.content}" 단어는 서버 전인원이 못씁')
            elif target ==LabeledTarget.ONLY_CERTAIN_MEMBERS:
                CensorshipManager.set_global(self.guild, self.content, False)
                await res.send_message(f'"{self.content}" 에 대한 지정 검열 설정')

        except PolicyNotFoundError:
            await res.send_message(f'이 메세지 띄워진 사이에 정책이 날라감')


class TargetSelectView(discord.ui.View):
    def __init__(self, guild: Guild, content: str):
        super().__init__()
        self.add_item(TargetSelect(guild, content))