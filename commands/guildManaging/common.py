import nextcord
from nextcord import SlashOption, Embed, String
from nextcord.ext import commands
from textwrap import dedent

# TODOTODOTOD 역할 제거 완성해라
from commonModule.embed_message import sendErrorEmbed, Color, sendCompleteEmbed, sendWarnEmbed
from commonModule.exceptions import GuildMismatchError
from main import PieBot

class CommonGuildManaging(commands.Cog):
    def __init__(self, bot):
        self.bot: PieBot = bot

    @nextcord.slash_command(name='관리자목록', description="관리자로 지정된 모든 맴버, 역할을 보여줍니다")
    async def adminList(self, interaction: nextcord.Interaction):
        guildAdminManager = self.bot.adminManager.getGuildAdminManager(interaction.guild)


        if not (allAdmins := guildAdminManager.getAllAdmins()):
            await sendWarnEmbed(interaction, warnTitle="AdminDoesNotExistWarning!",
                                description="해당 서버에 관리자와 관리자 역할이 없습니다")
            return

        embed = Embed(color=Color.SKY, title="이 서버의 관리자/관리자 역할들")

        adminsFieldContent = ".\n"

        for member in allAdmins:
            singleAdminField = str()

            memberName = member.nick if member.nick else member.name

            singleAdminField += "**" + memberName + "**\n"

            singleAdminField += "> 해당하는 역할: \n"
            adminRoles = guildAdminManager.getAdminRolesMemberHas(member)

            if not adminRoles:
                singleAdminField += "> `관리자 명령어로 지정된 관리자이며, 해당하는 역할은 없습니다`"
            else:
                singleAdminField += "> "
                for role in adminRoles:
                    singleAdminField += f"`{role.name}` "

            adminsFieldContent += singleAdminField + "\n\n"

        if 1024 < len(adminsFieldContent):
            adminsFieldContent = "`내용이 너무 많아 표시할수 없습니다`"

        embed.add_field(name="관리자 멤버: ", value=adminsFieldContent, inline=True)



        adminRolesFieldContent = str()

        if not guildAdminManager.adminRoles:
            adminRolesFieldContent += '`관리자 역할로 지정된 역할이 없습니다`'

        for adminRole in guildAdminManager.adminRoles:
            adminRolesFieldContent += f"`{adminRole.name}` "



        if 1024 < len(adminsFieldContent) and 1024 < len(adminRolesFieldContent):
            await sendErrorEmbed(interaction, "ContentSizeError!!!",
                                 description="내용이 너무 많아 표시할수 없습니다")
            return

        if 1024 < len(adminRolesFieldContent):
            adminRolesFieldContent = "`내용이 너무 많아 표시할수 없습니다`"

        embed.add_field(name="관리자 역할: ", value=adminRolesFieldContent, inline=True)



        await interaction.send(embed=embed)

    @nextcord.slash_command(name='관리자역할목록', description="관리자로 지정된 역할을 보여줍니다")
    async def adminRoleList(self, interaction: nextcord.Interaction):

        guildAdminManager = self.bot.adminManager.getGuildAdminManager(interaction.guild)

        adminRolesFieldContent = str()
        embed = Embed(color=Color.SKY, title="이 서버의 관리자 역할들")

        if not guildAdminManager.adminRoles:
            await sendWarnEmbed(interaction, warnTitle="AdminRoleDoesNotExistWarning!",
                                description=
                                "관리자로 지정된 역할이 없습니다")
            return

        for adminRole in guildAdminManager.adminRoles:
            adminRolesFieldContent += f"`{adminRole.name}` "

        if 1024 < len(adminRolesFieldContent):
            await sendErrorEmbed(interaction, "ContentSizeError!!!",
                                 description="내용이 너무 많아 표시할수 없습니다")
            return

        embed.add_field(name="관리자 역할: ", value=adminRolesFieldContent, inline=True)

        await interaction.send(embed=embed)



    @nextcord.slash_command(name='관리자', description=dedent('''
    파이봇의 서버 관리 기능을 사용할수 있는 사람을 설정합니다. 기본적으로 서버장이 관리자로 설정되어 있습니다''').strip())
    async def admin(self, interaction: nextcord.Interaction,
                    user: nextcord.ApplicationCommandOptionType.user
                    = SlashOption(name="맴버", description="새로 관리자로 임명할 사람을 지정합니다")):

        user: nextcord.User

        member = interaction.guild.get_member(user.id)

        if member is None:
            await sendErrorEmbed(interaction, "GuildMismatchError!!!",
                                 f"`{user.display_name}`은/는 해당 서버의 인원이 아닙니다!")

        guildAdminManager = self.bot.adminManager.getGuildAdminManager(interaction.guild)
        if not guildAdminManager.isAdmin(interaction.user): return

        memberName = member.nick if member.nick else member.name

        if guildAdminManager.isAdmin(member):
            await sendWarnEmbed(interaction, warnTitle="MemberAlreadyAdminWarning",
                                description=
                                f"맴버 `{memberName}`은/는 이미 해당 서버의 관리자 입니다")
            return

        self.bot.adminManager.getGuildAdminManager(interaction.guild).addAdmin(member)

        await sendCompleteEmbed(interaction,
                                f"맴버 `{memberName}`을/를 해당 서버의 관리자로 임명했습니다")

        self.bot.adminManager.save()

    @nextcord.slash_command(name='관리자역할', description=dedent('''
    파이봇의 서버 관리 기능을 사용할수 있는 역할을 지정합니다. 기본적으로 서버장이 이 명령어를 사용할수 있습니다'''))
    async def adminRole(self, interaction: nextcord.Interaction,
                        role: nextcord.ApplicationCommandOptionType.role
                        = SlashOption(name="역할", description="관리자가 될수 있는 역할을 지정합니다")):

        guildAdminManager = self.bot.adminManager.getGuildAdminManager(interaction.guild)
        if not guildAdminManager.isAdmin(interaction.user): return

        try:
            if guildAdminManager.isAdminRole(role):
                await sendWarnEmbed(interaction, warnTitle="RoleAlreadyAdminWarning!",
                                    description=f"`{role.name}`역할은 이미 관리자 역할입니다")
                return

            guildAdminManager.addRole(role)
            await sendCompleteEmbed(interaction, f"`{role.name}`를 관리자 역할로 지정합니다")

        except GuildMismatchError:
            await sendErrorEmbed(interaction, "GuildMismatchError!!!",
                                 f"역할 `{role.name}`은/는 해당 서버의 역할이 아닙니다!")

        self.bot.adminManager.save()



    @nextcord.slash_command(name='관리자제거', description=dedent('''탄핵 하라'''))
    async def rmAdmin(self, interaction: nextcord.Interaction,
                      user: nextcord.ApplicationCommandOptionType.user
                      = SlashOption(name="맴버", description="관리자에서 제거할 맴버를 지정합니다")):

        user: nextcord.User

        member = interaction.guild.get_member(user.id)

        if member is None:
            await sendErrorEmbed(interaction, "GuildMismatchError!!!",
                                 f"`{user.display_name}`은/는 해당 서버의 인원이 아닙니다!")

        guildAdminManager = self.bot.adminManager.getGuildAdminManager(interaction.guild)
        if not guildAdminManager.isAdmin(interaction.user): return

        memberName = member.nick if member.nick else member.name

        if not guildAdminManager.isAdmin(member):
            await sendErrorEmbed(interaction, errorTitle="KeyError!!!",
                           description=f"맴버 `{memberName}`은/는 해당 서버의 관리자가 아닙니다")
            return

        try:
            self.bot.adminManager.getGuildAdminManager(interaction.guild).rmAdmin(member)
        except KeyError: ...

        if guildAdminManager.isAdmin(member):
            roleNames = ", ".join(
                [f"`{rule.name}`" for rule in guildAdminManager.getAdminRolesMemberHas(member)]
            )
            embed = Embed(
                title="DuplicationRolePermissionWarning!",
                description=f"맴버 `{memberName}`의 역할인 {roleNames} 이/가 "
                            f"관리자 권한으로 지정되 있어, 관리자 제거가 불가능합니다.",
                color=Color.YELLOW
            )
            embed.set_footer(text=f"해당 유저의 관리자 권환을 회수할려면 `/관리자역할제거` 로 해당하는 역할을 제거해 주세요")
            await interaction.send(embed=embed)

            return

        await sendCompleteEmbed(interaction, f"맴버 `{memberName}`을/를 탄핵했습니다")

    @nextcord.slash_command(name='관리자역할제거', description=dedent('''
    파이봇의 서버 관리 기능을 사용할수 있는 역할을 지정합니다. 기본적으로 서버장이 이 명령어를 사용할수 있습니다'''))
    async def rmAdminRole(self, interaction: nextcord.Interaction,
                        role: nextcord.ApplicationCommandOptionType.role
                        = SlashOption(name="역할", description="관리자가 될수 있는 역할을 지정합니다")):

        guildAdminManager = self.bot.adminManager.getGuildAdminManager(interaction.guild)
        if not guildAdminManager.isAdmin(interaction.user): return

        try:
            if not guildAdminManager.isAdminRole(role):
                await sendWarnEmbed(interaction, warnTitle="KeyError!",
                                    description=f"`{role.name}`역할은 원래 관리자 역할이 아닙니다")
                return

            guildAdminManager.rmRole(role)
            await sendCompleteEmbed(interaction, f"`{role.name}`를 관리자 역할에서 제거했습니다")

        except GuildMismatchError:
            await sendErrorEmbed(interaction, "GuildMismatchError!!!",
                                 f"역할 `{role.name}`은/는 해당 서버의 역할이 아닙니다!")

        self.bot.adminManager.save()






def setup(bot: commands.Bot):
    bot.add_cog(CommonGuildManaging(bot))