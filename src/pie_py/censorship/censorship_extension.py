from enum import Enum
from typing import Literal

from aiohttp.abc import HTTPException
from discord.ext import commands
from discord import Member, Message

from .core.censorship import CensorshipManager
from .core.censorship.exceptions import DuplicateError, PolicyNotFoundError
from .target_select_ui import TargetSelectView


class AddFlags(commands.FlagConverter):
    content: str = commands.Flag(name='내용', description='검열 목록에 추가할 내용을 지정해 주세요')
    target_member: Member | None = commands.Flag(name='맴버', description='sadf')

class RmFlags(commands.FlagConverter):
    content: str = commands.Flag(name='내용', description='검열 목록에에서 제거할 내용을 지정해 주세요')
    target_member: Member | None = commands.Flag(name='맴버', description='sadf')

class TargetFlags(commands.FlagConverter):
    content: str = commands.Flag(name='내용', description='적용 대상을 설정할 검열 내용을 지정해 주세요')


class CensorshipExtension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.guild is not None:
            guild = message.guild

            for policy in CensorshipManager.get_guild_policies(guild):
                if policy.is_global:
                    if policy.content in message.content:

                        while True:
                            try:
                                await message.delete()
                                break
                            except HTTPException: pass
                        return
                else:
                    if (message.author in policy.target_members
                            and message.content in policy.content):

                        while True:
                            try:
                                await message.delete()
                                break
                            except HTTPException: pass
                        return


    @commands.hybrid_command(name='검열목록', description='이 서버에서 말하면교수척장분지형당하는거j')
    async def censorship_list(self, ctx: commands.Context):
        policies = CensorshipManager.get_guild_policies(ctx.guild)

        message = str()

        for policy in policies:
            if policy.is_global:
                message += f'content: "{policy.content}" | targets: 서버의 모두\n'
            else:
                member_names = [str(member) for member in policy.target_members]
                message += f'content: "{policy.content}" | targets: {", ".join(member_names)}\n' # TODO

        await ctx.send(message)

    @commands.hybrid_group(name='검열', description='검열 관리 명령어 모음')
    async def censorship(self, ctx: commands.Context): ...


    @censorship.command(name='추가')
    async def add(self, ctx: commands.Context, *, flags: RmFlags):
        if flags.target_member is None:
            try:
                CensorshipManager.add_policy(ctx.guild, flags.content, is_global=True)
                await ctx.send(f'검열 목록에 "{flags.content}" 추가함')

            except DuplicateError:
                await ctx.send('이미 서버에서 그거 검열 리스트로 올라가 있으')


        elif flags.target_member is not None:
            try:
                CensorshipManager.add_policy(ctx.guild, flags.content, is_global=False)
            except DuplicateError: pass

            try:
                CensorshipManager.add_member_policy(ctx.guild, flags.target_member, flags.content)
                await ctx.send(f'{flags.target_member} 는 이제 {flags.content} 못말함')
            except DuplicateError:
                policy = CensorshipManager.get_guild_policy(ctx.guild, flags.content)

                if policy.is_global:
                    await ctx.send("해당 유저에 대한 정책은 이미 있. 근데 단어 자체가 서버 공통 적용이라서 의미 없음 TODO")
                else:
                    await ctx.send("도데체 뭘 잘못한건진 모르겠는데 해당 유저는 이미 그걸로 검열 처먹음")


    @censorship.command(name='빼기')
    async def rm(self, ctx: commands.Context, *, flags: RmFlags):
        if flags.target_member is None:
            try:
                CensorshipManager.rm_policy(ctx.guild, flags.content)
                await ctx.send('검열 없엠')
            except PolicyNotFoundError:
                await ctx.send("이 길드엔 그런 검열단어 없읍")

        elif flags.target_member is not None:
            try:
                CensorshipManager.rm_member_policy(ctx.guild, flags.target_member, flags.content)
                await ctx.send('검열 없엠')
            except PolicyNotFoundError:
                await ctx.send(f'"{flags.target_member}" 에 대해 "{flags.content}" 로 검열 맥이는건 없음')


    @censorship.command(name='적용대상')
    async def target(self, ctx: commands.Context, *, flags: TargetFlags):
        try:
            CensorshipManager.get_guild_policy(ctx.guild, flags.content)

            await ctx.send(
                f'Select apply target for content: "{flags.content}"',
                view=TargetSelectView(ctx.guild, flags.content)
            )
        except PolicyNotFoundError:
            await ctx.send('그런 검열 정책은 없는뎁쇼')


async def setup(bot: commands.Bot):
    await bot.add_cog(CensorshipExtension(bot))

__all__ = [
    'setup'
]