from sqlalchemy import Column, BIGINT

from pie_py.db import Base


class CensorshipEnabledGuilds(Base):
    __tablename__ = "censorship_enabled_guilds"

    guild_id = Column(BIGINT, primary_key=True, autoincrement=False)