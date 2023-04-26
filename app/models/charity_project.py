from sqlalchemy import Column, String, Text

from app.core.db import Base, PreBaseCharity


class CharityProject(Base, PreBaseCharity):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
