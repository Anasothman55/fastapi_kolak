
from ..models.user import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Any
from sqlmodel import select
import  uuid
from fastapi import  status, HTTPException
from app.util.user_auth import  error_schema, create_access_token,verify_password_utils
from datetime import timedelta


class UserRepositoryServer:
  def __init__(self, db: AsyncSession):
    self.db = db
    self.model = UserModel
  async def _statement(self,  field: str, value: Any):
    statement = select(self.model).where(getattr(self.model, field) == value)
    result = await self.db.execute(statement)
    return result.scalars().first()

  async def get_by_email(self, email: str):
    return await self._statement("email", email)

  async def get_by_username(self, username: str):
    return await self._statement("username", username)

  async def get_by_uid(self, uid: uuid.UUID):
    return await self._statement("uid", uid)

class AuthenticationService:
  def __init__(self,db: AsyncSession):
    self.db = db
    self.user_repo = UserRepositoryServer(db)
    self.verify_password = verify_password_utils
  async def auth_unique_validation(self, email: str, username: str):
    errors = {}
    if existing_user := await self.user_repo.get_by_username(username):
      errors['username'] = error_schema("username", existing_user.username)

    if existing_user := await self.user_repo.get_by_email(email):
      errors['email'] = error_schema("email", existing_user.email)

    return errors

  async def authenticate_user(self, email: str, password: str) -> UserModel:
    user = await self.user_repo.get_by_email(str(email))
    if not user:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "User not found", "hint": "Please check the email address","loc":"email"}
      )

    if not verify_password_utils(password, user.hash_password):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "Invalid password", "hint": "Ensure the password is correct", "loc": "password"}
      )

    return user

class TokenService:
  def __init__(self, config):
    self.config = config

  async def create_token(self, token_data: dict) -> str:
    token_data = {
      **token_data,
      "jit": str(uuid.uuid4()),
      "fid": str(uuid.uuid4())
    }

    expires_delta = timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
      data=token_data,
      expires_delta=expires_delta
    )

  def set_cookie_token(self, response, token: str) -> None:
    response.set_cookie(
      key="access_token",
      value=token,
      httponly=True,
      expires=60 * 60,
      secure=True,  # Added secure flag for HTTPS
      samesite='lax'  # Added samesite protection
    )


