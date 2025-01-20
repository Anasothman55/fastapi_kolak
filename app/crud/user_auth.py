from ..models.user import UserModel
from ..service.user_auth import AuthenticationService, TokenService
from ..db.index import AsyncSession,get_db
from ..schemas.user_auth import UserBase, CreateUser, CreateIUserDict
from typing import Annotated
from fastapi import status,HTTPException, Depends, Response, Request
from ..util.user_auth import hash_password_utils,verify_password_utils,ValidationErrorWithUnique
from pydantic import ValidationError, EmailStr
from datetime import datetime, timezone, timedelta
from fastapi.responses import JSONResponse
from app.core.config import config


token_service = TokenService(config)


async def register_crud(
  register_model: CreateIUserDict,
  db: Annotated[AsyncSession, Depends(get_db)],
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
  try:
    auth_service = AuthenticationService(db)
    user = await auth_service.authenticate_user(email, password)

    user.last_login = datetime.now()
    await db.commit()

    user_token_dict = {"sub": str(user.uid), "email": user.email }
    token = await token_service.create_token(user_token_dict)
    token_service.set_cookie_token(response, token)

    return {"message": "Login successful"}

  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during user login: {str(e)}")


async def logout_user_crud( response: Response):
  response.delete_cookie("access_token")
  return {"detail": "User logged out"}


