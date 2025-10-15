from sqlalchemy import Column, Integer, BIGINT, Boolean, UniqueConstraint, String
from sqlalchemy.orm import relationship

from pie_py.db import Base

class CensorshipPolicy(Base):
    __tablename__ = "censorship_policies"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BIGINT, nullable=False)
    content = Column(String(256), nullable=False)
    is_global = Column(Boolean, nullable=False)

    target_members = relationship('CensorshipTargetMember', back_populates='policy')

    __table_args__ = (
        UniqueConstraint('guild_id', 'content', name='uq_policy'),
    )