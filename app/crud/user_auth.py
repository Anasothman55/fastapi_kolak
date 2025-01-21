from ..models.user import UserModel
from ..service.user_auth import AuthenticationService, TokenService
from ..db.index import AsyncSession, get_db
from ..schemas.user_auth import CreateUser, CreateIUserDict
from typing import Annotated
from fastapi import status,HTTPException, Response, Depends
from ..util.user_auth import hash_password_utils,ValidationErrorWithUnique
from pydantic import ValidationError
from datetime import datetime
from app.core.config import config





class UserAuthCrud:
  def __init__(
    self, db: AsyncSession, response: Response, token_services: TokenService, auth_service: AuthenticationService
  ):
    self.db = db
    self.response = response
    self._token_service = token_services
    self._auth_service = auth_service

  async def _set_auth_token(self, user: UserModel) -> None:
    user_token_dict = {"sub": str(user.uid), "email": user.email}
    token = await self._token_service.create_token(user_token_dict)
    self._token_service.set_cookie_token(self.response, token)


  async def _check_unique_constraints(self, email: str, username: str) :
    return await self._auth_service.auth_unique_validation(email, username)

  def _extract_unique_validation_errors(self, register_model: CreateIUserDict):
    email = getattr(register_model, 'email', '')
    username = getattr(register_model, 'username', '')
    return self._auth_service.auth_unique_validation(email, username)
  def _validate_and_prepare_user(self, register_model: CreateIUserDict):
    try:
      return CreateUser(**register_model.model_dump())
    except ValidationError as e:
      unique_errors = self._extract_unique_validation_errors(register_model)
      raise ValidationErrorWithUnique(
        pydantic_errors=e.errors(),
        unique_errors=unique_errors
      )
  async def register_crud( self, register_model: CreateIUserDict ):
    try:
      user = self._validate_and_prepare_user(register_model)
      unique_errors = await self._check_unique_constraints(str(user.email), user.username)
      if unique_errors:
        raise ValidationErrorWithUnique(unique_errors=unique_errors)

      hashing = hash_password_utils(register_model.password)
      user_data = register_model.model_dump(exclude={"password"})
      new_user = UserModel(**user_data, hash_password=hashing)
      new_user.last_login = datetime.now()
      self.db.add(new_user)
      await self.db.commit()

      user_token_dict = {"sub": str(new_user.uid), "email": new_user.email }
      token = await token_service.create_token(user_token_dict)
      token_service.set_cookie_token(self.response, token)

      return new_user

    except ValidationErrorWithUnique as e:
      raise e
    except Exception as e:
      await self.db.rollback()
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error during user registration: {str(e)}"
      )

  async def login_crud(self,email: str, password: str):
    user = await self._auth_service.authenticate_user(email, password)

    user.last_login = datetime.now()
    await self.db.commit()

    await self._set_auth_token(user)

    return {"message": "Login successful"}

  async def logout_user_crud(self):
    self.response.delete_cookie("access_token")
    return {"detail": "User logged out"}



token_service = TokenService(config)


async def register_crud(
  register_model: CreateIUserDict,
  db:AsyncSession,
  response: Response
):
  auth_service = AuthenticationService(db)
  try:
    try:
      user = CreateUser(**register_model.model_dump())
    except ValidationError as e:
      unique_errors = {}
      if hasattr(register_model, 'email') and hasattr(register_model, 'username'):
        email = str(getattr(register_model, 'email', ''))
        username = getattr(register_model, 'username', '')
        unique_errors = await auth_service.auth_unique_validation(email, username)

      raise ValidationErrorWithUnique(
        pydantic_errors=e.errors(),
        unique_errors=unique_errors
      )

    unique_errors = await auth_service.auth_unique_validation(str(user.email), user.username)
    if unique_errors:
      raise ValidationErrorWithUnique(unique_errors=unique_errors)

    hashing = hash_password_utils(register_model.password)
    user_data = register_model.model_dump(exclude={"password"})
    new_user = UserModel(**user_data, hash_password=hashing)
    new_user.last_login = datetime.now()
    db.add(new_user)
    await db.commit()

    user_token_dict = {"sub": str(new_user.uid), "email": new_user.email }
    token = await token_service.create_token(user_token_dict)
    token_service.set_cookie_token(response, token)

    return new_user

  except ValidationErrorWithUnique as e:
    raise e
  except Exception as e:
    await db.rollback()
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Error during user registration: {str(e)}"
    )


async def login_crud(db: AsyncSession, email: str, password: str, response: Response):
  auth_service = AuthenticationService(db)
  user = await auth_service.authenticate_user(email, password)

  user.last_login = datetime.now()
  await db.commit()

  user_token_dict = {"sub": str(user.uid), "email": user.email }
  token = await token_service.create_token(user_token_dict)
  token_service.set_cookie_token(response, token)

  return {"message": "Login successful"}


async def logout_user_crud( response: Response):
  response.delete_cookie("access_token")
  return {"detail": "User logged out"}


