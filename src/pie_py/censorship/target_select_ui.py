from __future__ import annotations

from collections.abc import tuple_iterator
from enum import Enum
from typing import Any

import discord.ui
from discord import Guild, Interaction, InteractionResponse, Embed

from pie_py.censorship.core.censorship_manager import CensorshipManager
from pie_py.censorship.core.censorship_manager.exceptions import PolicyNotFoundError
from pie_py.utils import theme
from pie_py.utils.template import send_error_embed


class LabeledTarget(Enum):
    ALL = ('서버의 모든 인원',)
    ONLY_CERTAIN_MEMBERS = ('지정된 특정 멤버만',)

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
            placeholder='검열이 적용될 대상 선택',
            min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: Interaction):
        target = LabeledTarget.get_target_by_label(self.values[0])
        res: InteractionResponse = interaction.response

        try:
            if target == LabeledTarget.ALL:
                await CensorshipManager.set_global(self.guild, self.content, True)
                await res.send_message(
                    embed=Embed(
                        description=f'이제 서버 전부가 `{self.content}` 단어를 사용하지 못합니다',
                        color=theme.OK_COLOR
                    ), ephemeral=True
                )

            elif target ==LabeledTarget.ONLY_CERTAIN_MEMBERS:
                await CensorshipManager.set_global(self.guild, self.content, False)
                await res.send_message(
                    embed=Embed(
                        description=f'이제 일부 멤버는 `{self.content}` 단어를 사용하지 못합니다',
                        color=theme.OK_COLOR
                    ), ephemeral=True
                )

        except PolicyNotFoundError:
            await res.send_message(
                embed=Embed(
                    title='PolicyNotFoundError',
                    description='이 선택창이 띄워진 사이에 해당 검열 정책이 삭제되었습니다',
                    color=theme.ERROR_COLOR
                ), ephemeral=True
            )


class TargetSelectView(discord.ui.View):
    def __init__(self, guild: Guild, content: str):
        super().__init__()
        self.add_item(TargetSelect(guild, content))