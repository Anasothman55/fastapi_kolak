from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_auth import register_crud, login_crud, logout_user_crud
from app.db.index import get_db
from app.dependencies.user_auth import get_current_user
from app.models.user import UserModel
from app.schemas.user_auth import UserBase, CreateUser, CreateIUserDict,UserLogin, GetFullUser
from typing import Annotated





auth_router = APIRouter(tags=["Auth"])



@auth_router.post("/register",response_model= UserBase, status_code= status.HTTP_201_CREATED)
async def register_router(
  data_model: CreateIUserDict,
  db: Annotated[AsyncSession, Depends(get_db)],
  response: Response
):
  result = await register_crud(data_model, db, response)
  return result


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_router(
  *,
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  response: Response,
  db: AsyncSession = Depends(get_db)
):
  result = await login_crud(db,form_data.username,form_data.password, response)
  return result


@auth_router.post("/logout", status_code= status.HTTP_202_ACCEPTED)
async def logout_router(response: Response, current_user: Annotated[dict, Depends(get_current_user)]):
  result = await logout_user_crud(response)
  return result


@auth_router.get("/me", response_model=GetFullUser, status_code=status.HTTP_200_OK)
async def get_user_me_router( current_user: Annotated[UserModel, Depends(get_current_user)]):
  return current_user






