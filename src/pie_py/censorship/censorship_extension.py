import logging

from aiohttp.abc import HTTPException
from discord.ext import commands
from discord import Member, Message, Embed, NotFound, app_commands

from .core.censorship_manager import CensorshipManager, CensorshipPolicy
from .core.censorship_manager.exceptions import DuplicateError, PolicyNotFoundError
from .core.text_converter import TextConverter, convert_funcs
from .target_select_ui import TargetSelectView
from pie_py.utils import theme
import asyncio


class AddFlags(commands.FlagConverter):
    content: str = commands.Flag(name='내용', description='검열 목록에 추가할 내용을 지정해 주세요')
    target_member: Member | None = commands.Flag(
        name='멤버', description='특정 멤버에게만 적용되게 할려때 기입해 주세요'
    )

class RmFlags(commands.FlagConverter):
    content: str = commands.Flag(name='내용', description='검열 목록에에서 제거할 내용을 지정해 주세요')
    target_member: Member | None = commands.Flag(
        name='멤버', description='특정 멤버에게만 적용되는 검열을 뺄때 기입해 주세요'
    )

class TargetFlags(commands.FlagConverter):
    content: str = commands.Flag(name='내용', description='적용 대상을 설정할 검열 내용을 지정해 주세요')

class ListFlags(commands.FlagConverter):
    member: Member | None = commands.Flag(name='멤버', description='특정 멤버의 금지어만 확인할려면 입력해 주세요')


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
        if message.guild is None: return

        if not await CensorshipManager.is_censorship_enabled(message.guild):
            return
        if message.author.bot or message.author.guild_permissions.manage_guild:
            return


        guild = message.guild

        for policy in await CensorshipManager.get_guild_policies(guild):
            if policy.is_global:
                if self.is_illegal(message.content, policy.content):
                    await self.censor_message(message, policy)
                    return

            else:
                if (message.author in policy.target_members
                        and self.is_illegal(message.content, policy.content)):
                    await self.censor_message(message, policy)
                    return

    @commands.Cog.listener()
    async def on_message_edit(self, _: Message, message: Message):
        if message.guild is None: return

        if not await CensorshipManager.is_censorship_enabled(message.guild):
            return
        if message.author.bot or message.author.guild_permissions.manage_guild:
            return


        guild = message.guild

        for policy in await CensorshipManager.get_guild_policies(guild):
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


    @commands.hybrid_command(name='금지어', description='이 서버의 금지어') # aliases
    async def forbidden_words(self, ctx: commands.Context):
        embed = Embed(
            title=f'서버 "{ctx.guild.name}" 의 금지어',
            description='표기된 단어, 유사한 단어또한 검열됩니다',
            color=theme.OK_COLOR
        )

        policies = [
            policy for policy in await CensorshipManager.get_guild_policies(ctx.guild)
            if policy.is_global or ctx.author in policy.target_members
        ]

        if policies:
            for policy in policies:
                embed.add_field(name=f'||`{policy.content}`||', value='')
        else:
            embed.add_field(name='', value='검열되는 단어가 없습니다')

        await ctx.send(embed=embed, ephemeral=True)


    @commands.hybrid_group(name='검열', description='검열 관리 명령어 모음')
    @app_commands.default_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True) # 슬래시 커맨드용 퍼미션 검사
    async def censorship(self, ctx: commands.Context): ...

    # 하위 명령어들

    @censorship.command(name='활성화', description='이 서버의 검열 기능을 활성화 합니다')
    @app_commands.default_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True) # 슬래시 커맨드용 퍼미션 검사
    async def enable(self, ctx: commands.Context):
        try:
            await CensorshipManager.enable_censorship(ctx.guild)
        except ValueError:
            await ctx.send(
                embed=Embed(
                    title='StateError',
                    description='이미 검열 기능이 활성화 되어 있습니다. '
                                '비활성화 할려면 `/검열 비활성화` 명령어를 사용해 주세요',
                    color=theme.ERROR_COLOR
                ), ephemeral=True
            )
        else:
            embed = Embed(
                title='이 서버의 검열 기능을 활성화 했습니다',
                description='`/검열 추가`, `/검열 빼기`, `/검열 적용대상`, `/검열 단어목록` 등의 명령어를 사용해 보세요. '
                            '`/검열 비활성화` 로 다시 비활성화 할수 있습니다',
                color=theme.OK_COLOR
            )
            embed.set_footer(text='관련 기능은 서버 관리 권한이 있는 맴버만 사용할수 있습니다. '
                                  '아직 검열기능 테스트 다 안함; 버그나면 디코 @t1h2e 로 연락좀')
            await ctx.send(embed=embed, ephemeral=True)


    @censorship.command(name='비활성화', description='이 서버의 검열 기능을 비활성화 합니다')
    @app_commands.default_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True) # 슬래시 커맨드용 퍼미션 검사
    async def disable(self, ctx: commands.Context):
        try:
            await CensorshipManager.disable_censorship(ctx.guild)
        except ValueError:
            await ctx.send(
                embed=Embed(
                    title='StateError',
                    description='이미 검열 기능이 비활성화 되어 있습니다. '
                                '활성화 할려면 `/검열 활성화` 명령어를 사용해 주세요',
                    color=theme.ERROR_COLOR
                ), ephemeral=True
            )
        else:
            await ctx.send(
                embed=Embed(
                    title='이 서버의 검열 기능을 비활성화 했습니다. ',
                    description='`/검열 활성화` 로 다시 활성화 할수 있습니다',
                    color=theme.OK_COLOR
                ), ephemeral=True
            )


    @censorship.command(
        name='추가', description='검열 목록에 단어를 추가합니다. 특정 유저만 검열받도록 설정할수도 있습니다'
    )
    @app_commands.default_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True) # 슬래시 커맨드용 퍼미션 검사
    async def add(self, ctx: commands.Context, *, flags: RmFlags):
        if flags.target_member is None:
            try:
                await CensorshipManager.add_policy(ctx.guild, flags.content, is_global=True)

            except DuplicateError:
                await ctx.send(
                    embed=Embed(
                        title='DuplicateError',
                        description='해당 단어가 이미 검열 목록에 있습니다'
                    ), ephemeral=True
                )

            else:
                await ctx.send(
                    embed=Embed(
                        description=f'검열 단어 "**{flags.content}**" 을/를 추가했습니다',
                        color=theme.OK_COLOR,
                    ), ephemeral=True
                )


        elif flags.target_member is not None:
            try:
                await CensorshipManager.add_policy(ctx.guild, flags.content, is_global=False)
            except DuplicateError: pass

            policy = await CensorshipManager.get_guild_policy(ctx.guild, flags.content)
            if policy.is_global:
                await ctx.send(
                    embed=Embed(
                        title='StateError',
                        description='해당 검열은 모든 멤버에게 적용되도록 설정되어 있습니다.'
                        '지정한 멤버에게만 적용할려면 `/검열 적용대상` 명령어를 사용해 주세요'
                    ), ephemeral=True
                )
                return

            try:
                await CensorshipManager.add_member_policy(ctx.guild, flags.target_member, flags.content)

            except DuplicateError:
                policy = await CensorshipManager.get_guild_policy(ctx.guild, flags.content)

                if policy.is_global:
                    embed = Embed(
                        title='DuplicateError',
                        description='해당 멤버에 대한 동일한 검열 정책이 이미 있습니다',
                    )
                    embed.set_footer(
                        text=
                        '하지만 해당 단어가 서버 전역으로 적용되도록 설정되어 있습니다'
                        '지정한 멤버에게만 적용할려면 /검열 적용대상 명령어를 사용해 주세요',
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                else:
                    await ctx.send(
                        embed=Embed(
                            title='DuplicateError',
                            description='해당 멤버에 대한 동일한 검열 정책이 이미 있습니다'
                        ), ephemeral=True
                    )

            else:
                await ctx.send(
                    embed=Embed(
                        description=f'<@{flags.target_member.id}> 멤버에게 {flags.content} 검열 청책을 추가했습니다'
                    ), ephemeral=True
                )


    @censorship.command(name='빼기', description='검열 목록에서 특정 단어를 제거합니다')
    @app_commands.default_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True) # 슬래시 커맨드용 퍼미션 검사
    async def rm(self, ctx: commands.Context, *, flags: RmFlags):
        if flags.target_member is None:
            try:
                await CensorshipManager.rm_policy(ctx.guild, flags.content)

            except PolicyNotFoundError:
                await ctx.send(
                    embed=Embed(
                        description='검열 목록에 해당 단어가 없습니다',
                        color=theme.OK_COLOR
                    ), ephemeral=True
                )

            else:
                await ctx.send(
                    embed=Embed(
                        description='검열 정책을 제거했습니다',
                        color=theme.OK_COLOR
                    ), ephemeral=True
                )

        elif flags.target_member is not None:
            try:
                await CensorshipManager.rm_member_policy(ctx.guild, flags.target_member, flags.content)

            except PolicyNotFoundError:
                await ctx.send(
                    embed=Embed(
                        description=f'<@{flags.target_member.id}> 멤버에 대해 해당 단어를 검열하는 정책이 없습니다',
                        color=theme.OK_COLOR
                    ), ephemeral=True
                )

            else:
                await ctx.send(
                    embed=Embed(
                        description='검열 정책을 제거했습니다',
                        color = theme.OK_COLOR
                    ), ephemeral=True
                )


    @censorship.command(
        name='적용대상', description='검열이 모든 멤버에게 적용될지, 특정 멤버에게만 적용될지 설정합니다'
    )
    @app_commands.default_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True) # 슬래시 커맨드용 퍼미션 검사
    async def target(self, ctx: commands.Context, *, flags: TargetFlags):
        try:
            policy = await CensorshipManager.get_guild_policy(ctx.guild, flags.content)

        except PolicyNotFoundError:
            await ctx.send(
                embed=Embed(title='PolicyNotFoundError', description='해당 단어는 검열 목록에 없습니다'),
                ephemeral=True
            )

        else:
            embed = Embed(
                description=f'"{flags.content}" 단어의 검열을 누굴 대상으로 적용할지 선택해 주세요',
                color=theme.OK_COLOR
            )
            if policy.is_global:
                embed.set_footer(text='원래 설정은 전체 적용입니다')
            else:
                embed.set_footer(text='원래 설정은 지정한 일부 멤버만 적용입니다')

            await ctx.send(
                embed=embed,
                view=TargetSelectView(ctx.guild, flags.content),
                ephemeral=True
            )


    @censorship.command(name='단어목록',description='검열되는 단어의 목록을 확인합니다. 관리자 전용입니다')
    @app_commands.default_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True) # 슬래시 커맨드용 퍼미션 검사
    async def list(self, ctx: commands.Context, *, flags: ListFlags):

        if flags.member is None:
            embed = Embed(
                title=f'서버 "{ctx.guild.name}" 의 금지어',
                description='표기된 단어, 유사한 단어또한 검열됩니다',
                color=theme.OK_COLOR
            )

            policies = await CensorshipManager.get_guild_policies(ctx.guild)

            if policies:
                for policy in policies:
                    field_name = f'||`{policy.content}`||'
                    field_value = '* **대상:** '

                    if policy.is_global:
                        field_value += '이 서버의 모두'
                    else:
                        if policy.target_members:
                            field_value += ', '.join([f'<@{member.id}>' for member in policy.target_members])
                        else:
                            field_value += '없음'

                    embed.add_field(name=field_name, value=field_value)
            else:
                embed.add_field(name='', value='검열되는 단어가 없습니다')

            await ctx.send(embed=embed, ephemeral=True)

        elif flags.member is not None:
            if flags.member.nick is not None:
                member_name = flags.member.nick
            else:
                member_name = flags.member.name

            embed = Embed(
                title=f'이 서버에서 멤버 "**{member_name}**" 의 금지어',
                description='표기된 단어, 유사한 단어또한 검열됩니다',
                color=theme.OK_COLOR
            )

            policies = [
                policy for policy in await CensorshipManager.get_guild_policies(ctx.guild)
                if policy.is_global or flags.member in policy.target_members
            ]

            if policies:
                for policy in policies:
                    embed.add_field(name=f'||`{policy.content}`||', value='')
            else:
                embed.add_field(name='', value='검열되는 단어가 없습니다')

            await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CensorshipExtension(bot))

__all__ = [
    'setup'
]