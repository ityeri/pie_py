from sqlalchemy import Column, Integer, Boolean, UniqueConstraint, Text
from sqlalchemy.orm import relationship

from pie_py.db import Base

class CensorshipPolicy(Base):
    __tablename__ = "censorship_policies"

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, nullable=False)
    is_global = Column(Boolean, nullable=False)
    content = Column(Text, nullable=False)

    target_users = relationship('CensorshipTargetUser', back_populates='policy')

    # __table_args__ = (
    #     UniqueConstraint('guild_id', 'content', name='uq_policy'),
    # ) 걍 있다고 치자 content 가 가변 어쩌구라셔 유니크 조건으로 못들어감 리더에서 걍 처리할 예정.