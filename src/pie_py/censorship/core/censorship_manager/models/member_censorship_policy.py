from sqlalchemy import Column, BIGINT, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from pie_py.db import Base


class MemberCensorshipPolicy(Base):
    __tablename__ = 'member_censorship_policies'

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT, nullable=False)
    origin_policy_id = Column(
        Integer,
        ForeignKey('censorship_policies.id', ondelete="CASCADE"),
        nullable=False
    )

    origin_policy = relationship(
        'CensorshipPolicy',
        back_populates='member_policies',
        passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'origin_policy_id', name='uq_member_policy'),
    )