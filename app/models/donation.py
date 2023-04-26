from sqlalchemy import Column, Integer, Text, ForeignKey

from app.core.db import Base, PreBaseCharity


class Donation(Base, PreBaseCharity):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
