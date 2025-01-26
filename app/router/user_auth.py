from fastapi import APIRouter, status, HTTPException, Depends, Response, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from app.crud.user_auth import  UserAuthCrud
from app.db.index import get_db,AsyncSession
from app.dependencies.user_auth import get_current_user,get_user_auth_crud
from app.models.model import UserModel
from app.schemas.user_auth import UserBase ,CreateIUserDict, GetFullUser
from typing import Annotated
from rich import print
import json



auth_router = APIRouter(tags=["Auth"])




@auth_router.post("/register",response_model=UserBase, status_code= status.HTTP_201_CREATED)
async def register_router(
  data_model: Annotated[CreateIUserDict, Form()],
  user_auth_crud: Annotated[UserAuthCrud, Depends(get_user_auth_crud)]
):
  print(data_model.model_dump())
  result = await user_auth_crud.register_crud(data_model)
  return result


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_router(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  user_auth_crud: Annotated[UserAuthCrud, Depends(get_user_auth_crud)]
):
  email = form_data.username
  result = await user_auth_crud.login_crud(email,form_data.password)
  return result


@auth_router.post("/logout", status_code= status.HTTP_202_ACCEPTED)
async def logout_router(
  current_user: Annotated[dict, Depends(get_current_user)],
  user_auth_crud: Annotated[UserAuthCrud, Depends(get_user_auth_crud)]
):
  result = await user_auth_crud.logout_user_crud()
  return result


@auth_router.get("/me", response_model=GetFullUser, status_code=status.HTTP_200_OK)
async def get_user_me_router( current_user: Annotated[UserModel, Depends(get_current_user)]):
  json_data = jsonable_encoder(current_user)
  return json_data




