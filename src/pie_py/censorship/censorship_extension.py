import logging

from aiohttp.abc import HTTPException
from discord.ext import commands
from discord import Member, Message, Embed, NotFound

from .core.censorship_manager import CensorshipManager, CensorshipPolicy
from .core.censorship_manager.exceptions import DuplicateError, PolicyNotFoundError
from .core.text_converter import TextConverter, convert_funcs
from .target_select_ui import TargetSelectView
from pie_py.utils import theme
from ..utils.template import send_error_embed


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

        self.censored_text_converter: TextConverter = TextConverter(
            [
                convert_funcs.replace_sangjamo,
                convert_funcs.remove_special_char,
                convert_funcs.filter_chosung_only,
                convert_funcs.filter_hangul_only,
                convert_funcs.filter_complete_hangul_only,
                convert_funcs.filter_alphabet_only,
                convert_funcs.to_lower_case,
                convert_funcs.remove_space_char
            ], 4
        )
        self.message_converter: TextConverter = TextConverter(
            [
                convert_funcs.replace_sangjamo,
                convert_funcs.remove_special_char,
                # convert_funcs.filter_chosung_only,
                convert_funcs.filter_hangul_only,
                convert_funcs.filter_complete_hangul_only,
                convert_funcs.filter_alphabet_only, # TODO 확인 함 해봐야 할드t
                convert_funcs.to_lower_case,
                convert_funcs.remove_space_char
            ], 3
        )


    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.guild is not None:
            guild = message.guild

            for policy in CensorshipManager.get_guild_policies(guild):
                if policy.is_global:
                    if self.is_illegal(message.content, policy.content):
                        await self.censor_message(message, policy)
                        return

                else:
                    if (message.author in policy.target_members
                            and self.is_illegal(message.content, policy.content)):
                        await self.censor_message(message, policy)
                        return

    async def censor_message(self, message: Message, policy: CensorshipPolicy):
        logging.info(
            f'Message id: {message.id}, message content: "{message.content}", will censor by policy: {policy}'
        )
        while True:
            try:
                await message.delete()
                break
            except HTTPException:
                pass
            except NotFound:
                pass

    def is_illegal(self, text: str, censored_text: str) -> bool:
        if censored_text in text:
            return True

        for sub_text in self.message_converter.get_converted_texts(text):
            for sub_content in self.censored_text_converter.get_converted_texts(censored_text):

                if not sub_text or not sub_content: # sub_text 또는 sub_content 가 빈 문자열이면
                    continue
                elif (
                        not convert_funcs.remove_space_char(sub_text) or
                        not convert_funcs.remove_space_char(sub_content)
                ): # sub_text 또는 sub_content 가 공백 문자로만 이뤄져 있으면
                    continue

                if sub_content in sub_text:
                    return True

        return False


    @commands.hybrid_command(name='검열목록', description='이 서버에서 말하면교수척장분지형당하는거j')
    async def censorship_list(self, ctx: commands.Context):
        await self.censorship_list_for_admin(ctx)
        await self.censorship_list_for_user(ctx)

    @commands.hybrid_command(name='금지어', description='이 서버에서 말하면교수척장분지형당하는거j') # aliases
    async def forbidden_words(self, ctx: commands.Context):
        await self.censorship_list(ctx)


    async def censorship_list_for_admin(self, ctx: commands.Context):
        embed = Embed(
            title=f'서버 "{ctx.guild.name}" 의 금지어',
            description='표기된 단어, 유사한 단어또한 검열됩니다',
            color=theme.OK_COLOR
        )

        for policy in CensorshipManager.get_guild_policies(ctx.guild):
            field_name = f'"||`{policy.content}`||"'
            field_value = '* **대상:** '

            if policy.is_global:
                field_value += '이 서버의 모두'
            else:
                field_value += ', '.join([f'<@{member.id}>' for member in policy.target_members])

            embed.add_field(name=field_name, value=field_value)

        await ctx.send(embed=embed)

    async def censorship_list_for_user(self, ctx: commands.Context):
        user_censored_contents: list[str] = list()

        for policy in CensorshipManager.get_guild_policies(ctx.guild):
            if policy.is_global:
                user_censored_contents.append(policy.content)
            else:
                if ctx.author in policy.target_members:
                    user_censored_contents.append(policy.content)

        embed = Embed(
            title=f'서버 "{ctx.guild.name}" 의 금지어',
            description='표기된 단어, 유사한 단어또한 검열됩니다',
            color=theme.OK_COLOR
        )

        for content in user_censored_contents:
            embed.add_field(name=f'"||`{content}`||"', value='')

        await ctx.send(embed=embed)


    @commands.hybrid_group(name='검열', description='검열 관리 명령어 모음')
    async def censorship(self, ctx: commands.Context): ...


    @censorship.command(name='추가')
    async def add(self, ctx: commands.Context, *, flags: RmFlags):
        if flags.target_member is None:
            try:
                CensorshipManager.add_policy(ctx.guild, flags.content, is_global=True)

            except DuplicateError:
                await send_error_embed(
                    ctx, 'DuplicateError',
                    description='해당 단어가 이미 검열 목록에 있습니다'
                )

            else:
                await ctx.send(embed=Embed(
                    description=f'검열 단어 "**{flags.content}**" 을/를 추가했습니다',
                    color=theme.OK_COLOR
                ))


        elif flags.target_member is not None:
            try:
                CensorshipManager.add_policy(ctx.guild, flags.content, is_global=False)
            except DuplicateError: pass

            try:
                CensorshipManager.add_member_policy(ctx.guild, flags.target_member, flags.content)

            except DuplicateError:
                policy = CensorshipManager.get_guild_policy(ctx.guild, flags.content)

                if policy.is_global:
                    await send_error_embed(
                        ctx, 'DuplicateError',
                        description='해당 맴버에 대한 동일한 검열 정책이 이미 있습니다',
                        footer=
                            '하지만 해당 단어가 서버 전역으로 적용되도록 설정되어 있습니다'
                            '지정한 맴버에게만 정책을 적용하도록 할려면 `/검열 적용대상 명령어를 사용해 주세요'
                    )
                else:
                    await send_error_embed(
                        ctx, 'DuplicateError',
                        description='해당 맴버에 대한 동일한 검열 정책이 이미 있습니다'
                    )

            else:
                await ctx.send(embed=Embed(
                    description=f'<@{flags.target_member.id}> 맴버에게 {flags.content} 검열 청책을 추가했습니다'
                ))


    @censorship.command(name='빼기')
    async def rm(self, ctx: commands.Context, *, flags: RmFlags):
        if flags.target_member is None:
            try:
                CensorshipManager.rm_policy(ctx.guild, flags.content)

            except PolicyNotFoundError:
                await ctx.send(embed=Embed(
                    description='검열 목록에 해당 단어가 없습니다',
                    color=theme.OK_COLOR
                ))

            else:
                await ctx.send(embed=Embed(
                    description='검열 정책을 제거했습니다',
                    color=theme.OK_COLOR
                ))

        elif flags.target_member is not None:
            try:
                CensorshipManager.rm_member_policy(ctx.guild, flags.target_member, flags.content)

            except PolicyNotFoundError:
                await ctx.send(embed=Embed(
                    description=f'<@{flags.target_member.id}> 맴버에 대해 해당 단어를 검열하는 정책이 없습니다',
                    color=theme.OK_COLOR
                ))

            else:
                await ctx.send(embed=Embed(
                    description='검열 정책을 제거했습니다',
                    color = theme.OK_COLOR
                ))


    @censorship.command(name='적용대상')
    async def target(self, ctx: commands.Context, *, flags: TargetFlags):
        try:
            CensorshipManager.get_guild_policy(ctx.guild, flags.content)

        except PolicyNotFoundError:
            await send_error_embed(
                ctx, 'PolicyNotFoundError',
                '해당 단어는 검열 목록에 없습니다'
            )

        else:
            await ctx.send(
                embed=Embed(
                    description=f'"{flags.content}" 단어의 검열을 누굴 대상으로 적용할지 선택해 주세요',
                    color=theme.OK_COLOR
                ),
                view=TargetSelectView(ctx.guild, flags.content)
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(CensorshipExtension(bot))

__all__ = [
    'setup'
]