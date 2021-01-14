from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from AuthService import settings


engine = create_engine(
    settings.SQLALCHEMY_DB_URL, echo=True if settings.DEBUG else False
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
