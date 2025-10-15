from sqlalchemy import Column, BIGINT, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from pie_py.db import Base


class CensorshipTargetMember(Base):
    __tablename__ = "censorship_target_members"

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT, nullable=False)
    guild_id = Column(BIGINT, nullable=False)
    policy_id = Column(Integer, ForeignKey('censorship_policies.id'), nullable=False)

    policy = relationship('CensorshipPolicy', back_populates='target_members')

    __table_args__ = (
        UniqueConstraint('user_id', 'guild_id', 'policy_id', name='uq_target_member'),
    )