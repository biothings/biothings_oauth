import enum
import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import (
    # Column Types
    Integer, String, DateTime, ForeignKey, Boolean,
    # Other
    Column, Enum
)

from AuthService.database import Base


class BaseModel:
    """
    Contains the common fields for models.
    """
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)


class User(Base):
    """
    Represents a user to be authenticated.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64))
    identity_provider = Column(String(255))
    identity_provider_user_id = Column(Integer)

    clients = relationship("Client", back_populates="user")

    def __str__(self):
        return self.username


class Api(Base, BaseModel):
    """
    Represents an API to be protected.
    """
    __tablename__ = "apis"

    name = Column(String(256))
    identifier = Column(String(256), unique=True, nullable=False)
    description = Column(String(512))

    scopes = relationship("Scope", back_populates="api", cascade="all, delete")
    clients = relationship("ClientApi", back_populates="api")

    def __str__(self):
        return f"'{self.name}' - ({self.identifier})"


class Scope(Base, BaseModel):
    """
    Represents a scope to be granted to a user on an API.
    """
    __tablename__ = "scopes"

    name = Column(String(256))
    description = Column(String(512))
    api_id = Column(Integer, ForeignKey(Api.id))

    api = relationship(Api, back_populates="scopes")
    client_apis = relationship("ClientApiScope", back_populates="scope")

    def __str__(self):
        return self.name


class ClientType(enum.Enum):
    """
    Type of clients.
    """
    NATIVE = "Native"
    SINGLE_PAGE_WEB_APP = "Single Page Web App"
    REGULAR_WEB_APP = "Regular Web App"
    MACHINE_TO_MACHINE_APP = "Machine To Machine App"


class Client(Base, BaseModel):
    """
    Represents a client for a user.
    """
    __tablename__ = "clients"

    client_id = Column(String(512), nullable=False)
    client_secret = Column(String(512), nullable=False)
    name = Column(String(256))
    type = Column(Enum(ClientType))
    authorized = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)

    user = relationship(User, back_populates="clients")
    apis = relationship(
        "ClientApi", back_populates="client", cascade="all, delete"
    )

    def __str__(self):
        return self.name


class ClientApi(Base):
    """
    Association table for Client and Api tables.
    """
    __tablename__ = "client_apis"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey(Client.id))
    api_id = Column(Integer, ForeignKey(Api.id))

    scopes = relationship("ClientApiScope", back_populates="client_api")
    client = relationship(Client, back_populates="apis")
    api = relationship(Api, back_populates="clients")


class ClientApiScope(Base):
    """
    Association table for ClientApi and Scope tables.
    """
    __tablename__ = "client_api_scopes"

    client_api_id = Column(Integer, ForeignKey(ClientApi.id), primary_key=True)
    scope_id = Column(Integer, ForeignKey(Scope.id), primary_key=True)

    client_api = relationship(ClientApi, back_populates="scopes")
    scope = relationship(Scope, back_populates="client_apis")
