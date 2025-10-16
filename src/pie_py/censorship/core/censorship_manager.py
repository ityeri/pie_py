from discord import Guild, Member
from discord.ext import commands
from sqlalchemy.exc import IntegrityError

from . import censorship_repository as repo
from .censorship_policy import CensorshipPolicy
from .censorship_repository import MemberCensorshipPolicy
from .exceptions import PolicyError, DuplicateError, PolicyNotFoundError
from pie_py.db import get_session_instance
from sqlalchemy import select, and_


class CensorshipManager:

    @staticmethod
    def add_policy(guild: Guild, content: str, is_global: bool):
        with get_session_instance() as session:
            new_policy = repo.CensorshipPolicy(guild_id=guild.id, content=content, is_global=is_global)

            try:
                session.add(new_policy)
                session.commit()
            except IntegrityError:
                raise DuplicateError("해당 정책이 이미 있습니다")

    @staticmethod
    def rm_policy(guild: Guild, content: str):
        with get_session_instance() as session:
            policy = session.scalars(select(repo.CensorshipPolicy).where(
                and_(
                    repo.CensorshipPolicy.guild_id == guild.id,
                    repo.CensorshipPolicy.content == content
                )
            )).first()

            if policy is None:
                raise PolicyNotFoundError("해당 길드에 해당 컨텐츠를 검열하는 정책이 없습니다")

            session.delete(policy)
            session.commit()


    @staticmethod
    def add_member_policy(guild: Guild, target_member: Member, content: str):
        if guild.id != target_member.guild.id:
            raise ValueError("지정된 맴버가 해당 길드에 속하지 않습니다")

        with get_session_instance() as session:
            policy = session.scalars(select(repo.CensorshipPolicy).where(
                and_(
                    repo.CensorshipPolicy.guild_id == guild.id,
                    repo.CensorshipPolicy.content == content
                )
            )).first()

            if policy is None:
                raise PolicyNotFoundError("해당 길드에 해당 컨텐츠를 검열하는 정책이 없습니다")

            new_member_policy = repo.MemberCensorshipPolicy(user_id=target_member.id)
            new_member_policy.origin_policy = policy

            try:
                session.add(new_member_policy)
                session.commit()
            except IntegrityError:
                raise DuplicateError("해당 유저의 동일한 길드에 대한 동일한 정책이 이미 있습니다")

    @staticmethod
    def rm_member_policy(guild: Guild, target_member: Member, content: str):
        with get_session_instance() as session:
            policy = session.scalars(select(repo.CensorshipPolicy).where(
                and_(
                    repo.CensorshipPolicy.guild_id == guild.id,
                    repo.CensorshipPolicy.content == content
                )
            )).first()

            if policy is None:
                raise PolicyNotFoundError("해당 길드에 해당 컨텐츠를 검열하는 정책이 없습니다")

            member_policy = session.scalars(select(repo.MemberCensorshipPolicy).where(
                and_(
                    repo.MemberCensorshipPolicy.user_id == target_member.id,
                    repo.MemberCensorshipPolicy.origin_policy_id == policy.id
                )
            )).first()

            if member_policy is None:
                raise PolicyNotFoundError("이 길드에서 입력받은 맴버는 해당 컨텐츠의 검열 대상이 아닙니다")

            session.delete(member_policy)
            session.commit()

    @staticmethod
    def get_guild_policies(guild: Guild) -> list[CensorshipPolicy]:
        with get_session_instance() as session:
            polices: list[CensorshipPolicy] = list()

            for policy_row in \
                    session.scalars(select(repo.CensorshipPolicy).where(
                        repo.CensorshipPolicy.guild_id == guild.id)):

                if not policy_row.is_global:
                    member_policies: list[MemberCensorshipPolicy] = policy_row.member_policies
                    target_members = [guild.get_member(member_policy.user_id) for member_policy in member_policies]
                elif policy_row.is_global:
                    target_members = None

                polices.append(
                    CensorshipPolicy(
                        guild=guild,
                        content=policy_row.content,
                        is_global=policy_row.is_global,
                        target_members=target_members
                    )
                )

            return polices

    @staticmethod
    def set_global(guild: Guild, content: str, is_global: bool):
        with get_session_instance() as session:
            policy = session.scalars(select(repo.CensorshipPolicy).where(
                and_(
                    repo.CensorshipPolicy.guild_id == guild.id,
                    repo.CensorshipPolicy.content == content
                )
            )).first()

            if policy is None:
                raise PolicyNotFoundError("해당 길드에 해당 컨텐츠를 검열하는 정책이 없습니다")

            policy.is_global = is_global
            session.commit()