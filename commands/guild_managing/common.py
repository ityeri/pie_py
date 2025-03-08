import nextcord
from nextcord import SlashOption, Embed, String
from nextcord.ext import commands
from textwrap import dedent

from common_module.embed_message import send_error_embed, Color, send_complete_embed, send_warn_embed
from common_module.exceptions import GuildMismatchError
from main import PieBot

class CommonGuildManaging(commands.Cog):
    def __init__(self, bot):
        self.bot: PieBot = bot

    @nextcord.slash_command(name='관리자목록', description="관리자로 지정된 모든 맴버, 역할을 보여줍니다")
    async def admin_list(self, interaction: nextcord.Interaction):
        guild_admin_manager = self.bot.admin_manager.get_guild_admin_manager(interaction.guild)


        if not (all_admins := guild_admin_manager.get_all_admins()):
            await send_warn_embed(interaction, warn_title="AdminDoesNotExistWarning!",
                                  description="해당 서버에 관리자와 관리자 역할이 없습니다")
            return

        embed = Embed(color=Color.SKY, title="이 서버의 관리자/관리자 역할들")

        admins_field_content = ".\n"

        for member in all_admins:
            single_admin_field = str()

            member_name = member.nick if member.nick else member.name

            single_admin_field += "**" + member_name + "**\n"

            single_admin_field += "> 해당하는 역할: \n"
            admin_roles = guild_admin_manager.get_admin_roles_member_has(member)

            if not admin_roles:
                single_admin_field += "> `관리자 명령어로 지정된 관리자이며, 해당하는 역할은 없습니다`"
            else:
                single_admin_field += "> "
                for role in admin_roles:
                    single_admin_field += f"`{role.name}` "

            admins_field_content += single_admin_field + "\n\n"

        if 1024 < len(admins_field_content):
            admins_field_content = "`내용이 너무 많아 표시할수 없습니다`"

        embed.add_field(name="관리자 멤버: ", value=admins_field_content, inline=True)



        admin_roles_field_content = str()

        if not guild_admin_manager.admin_roles:
            admin_roles_field_content += '`관리자 역할로 지정된 역할이 없습니다`'

        for adminRole in guild_admin_manager.admin_roles:
            admin_roles_field_content += f"`{adminRole.name}` "



        if 1024 < len(admins_field_content) and 1024 < len(admin_roles_field_content):
            await send_error_embed(interaction, "ContentSizeError!!!",
                                   description="내용이 너무 많아 표시할수 없습니다")
            return

        if 1024 < len(admin_roles_field_content):
            admin_roles_field_content = "`내용이 너무 많아 표시할수 없습니다`"

        embed.add_field(name="관리자 역할: ", value=admin_roles_field_content, inline=True)



        await interaction.send(embed=embed)

    @nextcord.slash_command(name='관리자역할목록', description="관리자로 지정된 역할을 보여줍니다")
    async def admin_role_list(self, interaction: nextcord.Interaction):

        guild_admin_manager = self.bot.admin_manager.get_guild_admin_manager(interaction.guild)

        admin_roles_field_content = str()
        embed = Embed(color=Color.SKY, title="이 서버의 관리자 역할들")

        if not guild_admin_manager.admin_roles:
            await send_warn_embed(interaction, warn_title="AdminRoleDoesNotExistWarning!",
                                  description=
                                "관리자로 지정된 역할이 없습니다")
            return

        for admin_role in guild_admin_manager.admin_roles:
            admin_roles_field_content += f"`{admin_role.name}` "

        if 1024 < len(admin_roles_field_content):
            await send_error_embed(interaction, "ContentSizeError!!!",
                                   description="내용이 너무 많아 표시할수 없습니다")
            return

        embed.add_field(name="관리자 역할: ", value=admin_roles_field_content, inline=True)

        await interaction.send(embed=embed)



    @nextcord.slash_command(name='관리자', description=dedent('''
    파이봇의 서버 관리 기능을 사용할수 있는 사람을 설정합니다. 기본적으로 서버장이 관리자로 설정되어 있습니다''').strip())
    async def admin(self, interaction: nextcord.Interaction,
                    user: nextcord.ApplicationCommandOptionType.user
                    = SlashOption(name="맴버", description="새로 관리자로 임명할 사람을 지정합니다")):

        user: nextcord.User

        member = interaction.guild.get_member(user.id)

        if member is None:
            await send_error_embed(interaction, "GuildMismatchError!!!",
                                 f"`{user.display_name}`은/는 해당 서버의 인원이 아닙니다!")

        guild_admin_manager = self.bot.admin_manager.get_guild_admin_manager(interaction.guild)
        if not guild_admin_manager.is_admin(interaction.user): return

        member_name = member.nick if member.nick else member.name

        if guild_admin_manager.is_admin(member):
            await send_warn_embed(interaction, warn_title="MemberAlreadyAdminWarning",
                                  description=
                                f"맴버 `{member_name}`은/는 이미 해당 서버의 관리자 입니다")
            return

        self.bot.admin_manager.get_guild_admin_manager(interaction.guild).add_admin(member)

        await send_complete_embed(interaction,
                                  description=f"맴버 `{member_name}`을/를 해당 서버의 관리자로 임명했습니다")

        self.bot.admin_manager.save()

    @nextcord.slash_command(name='관리자역할', description=dedent('''
    파이봇의 서버 관리 기능을 사용할수 있는 역할을 지정합니다. 기본적으로 서버장이 이 명령어를 사용할수 있습니다'''))
    async def admin_role(self, interaction: nextcord.Interaction,
                         role: nextcord.ApplicationCommandOptionType.role
                        = SlashOption(name="역할", description="관리자가 될수 있는 역할을 지정합니다")):

        guild_admin_manager = self.bot.admin_manager.get_guild_admin_manager(interaction.guild)
        if not guild_admin_manager.is_admin(interaction.user): return

        try:
            if guild_admin_manager.is_admin_role(role):
                await send_warn_embed(interaction, warn_title="RoleAlreadyAdminWarning!",
                                      description=f"`{role.name}`역할은 이미 관리자 역할입니다")
                return

            guild_admin_manager.add_role(role)
            await send_complete_embed(interaction, description=f"`{role.name}`를 관리자 역할로 지정합니다")

        except GuildMismatchError:
            await send_error_embed(interaction, "GuildMismatchError!!!",
                                 f"역할 `{role.name}`은/는 해당 서버의 역할이 아닙니다!")

        self.bot.admin_manager.save()



    @nextcord.slash_command(name='관리자제거', description=dedent('''탄핵 하라'''))
    async def rm_admin(self, interaction: nextcord.Interaction,
                       user: nextcord.ApplicationCommandOptionType.user
                      = SlashOption(name="맴버", description="관리자에서 제거할 맴버를 지정합니다")):

        user: nextcord.User

        member = interaction.guild.get_member(user.id)

        if member is None:
            await send_error_embed(interaction, "GuildMismatchError!!!",
                                 f"`{user.display_name}`은/는 해당 서버의 인원이 아닙니다!")

        guild_admin_manager = self.bot.admin_manager.get_guild_admin_manager(interaction.guild)
        if not guild_admin_manager.is_admin(interaction.user): return

        member_name = member.nick if member.nick else member.name

        if not guild_admin_manager.is_admin(member):
            await send_error_embed(interaction, error_title="KeyError!!!",
                                   description=f"맴버 `{member_name}`은/는 해당 서버의 관리자가 아닙니다")
            return

        try:
            self.bot.admin_manager.get_guild_admin_manager(interaction.guild).rm_admin(member)
        except KeyError: ...

        if guild_admin_manager.is_admin(member):
            role_names = ", ".join(
                [f"`{rule.name}`" for rule in guild_admin_manager.get_admin_roles_member_has(member)]
            )
            embed = Embed(
                title="DuplicationRolePermissionWarning!",
                description=f"맴버 `{member_name}`의 역할인 {role_names} 이/가 "
                            f"관리자 권한으로 지정되 있어, 관리자 제거가 불가능합니다.",
                color=Color.YELLOW
            )
            embed.set_footer(text=f"해당 유저의 관리자 권환을 회수할려면 `/관리자역할제거` 로 해당하는 역할을 제거해 주세요")
            await interaction.send(embed=embed)

            return

        await send_complete_embed(interaction, description=f"맴버 `{member_name}`을/를 탄핵했습니다")

    @nextcord.slash_command(name='관리자역할제거', description=dedent('''
    파이봇의 서버 관리 기능을 사용할수 있는 역할을 지정합니다. 기본적으로 서버장이 이 명령어를 사용할수 있습니다'''))
    async def rm_admin_role(self, interaction: nextcord.Interaction,
                            role: nextcord.ApplicationCommandOptionType.role
                        = SlashOption(name="역할", description="관리자가 될수 있는 역할을 지정합니다")):

        guild_admin_manager = self.bot.admin_manager.get_guild_admin_manager(interaction.guild)
        if not guild_admin_manager.is_admin(interaction.user): return

        try:
            if not guild_admin_manager.is_admin_role(role):
                await send_warn_embed(interaction, warn_title="KeyError!",
                                      description=f"`{role.name}`역할은 원래 관리자 역할이 아닙니다")
                return

            guild_admin_manager.rm_role(role)
            await send_complete_embed(interaction, description=f"`{role.name}`를 관리자 역할에서 제거했습니다")

        except GuildMismatchError:
            await send_error_embed(interaction, "GuildMismatchError!!!",
                                 f"역할 `{role.name}`은/는 해당 서버의 역할이 아닙니다!")

        self.bot.admin_manager.save()






def setup(bot: commands.Bot):
    bot.add_cog(CommonGuildManaging(bot))