from sqlalchemy import Column, Integer, String

from AuthService.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    nickname = Column(String(50))

    def __str__(self):
        return self.name
