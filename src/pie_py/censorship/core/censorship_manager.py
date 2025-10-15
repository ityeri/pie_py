from discord import Guild, Member
from discord.ext import commands
from . import censorship_repository as repo
from ... import db


class CensorshipManager:

    @staticmethod
    def add_policy(guild: Guild, content: str, is_global: bool, target_members: list[Member] | None=None):
        with db.get_session_instance() as session:
            new_policy = repo.CensorshipPolicy(guild_id=guild.id, content=content, is_global=is_global)

            target_member_rows: list[repo.CensorshipTargetMember] | None = None

            if not is_global:
                target_member_rows = list()

                for member in target_members:
                    if member.guild != guild:
                        raise ValueError('target_members 에 지정된 맴버는 모두 인자로 전달된 guild 에 소속되어 있어야 합니다')
                    else:
                        new_row = repo.CensorshipTargetMember(user_id=member.id, guild_id=guild.id)
                        new_row.policy = new_policy
                        target_member_rows.append(new_row)

            session.add(new_policy)
            if target_member_rows:
                session.add_all(target_member_rows)

            session.commit()