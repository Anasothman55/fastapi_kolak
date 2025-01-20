from sqlmodel import SQLModel,Field,Column, Relationship
from datetime import datetime, date,timezone
import sqlalchemy.dialects.postgresql as pg
import uuid
from typing import Optional, List
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class RoleBase(str,Enum):
  user = "user"
  admin = "admin"
  superuser = "superuser"
  


class UserModel(SQLModel, table=True):
  __tablename__ = 'usermodels'
  
  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )
  username: str = Field(unique=True, index=True)
  email: str = Field(unique=True, index=True)
  first_name: str = Field(index=True)
  last_name: str = Field(index=True)
  role: str = Field(sa_column=Column(SQLEnum(RoleBase), default=RoleBase.user))
  is_active: bool = Field(default = True)
  hash_password : str = Field(exclude=True)
  last_login: datetime = Field(nullable= True)
  created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc)))
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))
  )


  def __repr__(self):
    return f"<Book {self.username}>"
