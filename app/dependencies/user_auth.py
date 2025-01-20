from typing import Annotated

from sqlalchemy.util.langhelpers import repr_tuple_names

from app.models.user import UserModel
from app.service.user_auth import UserRepositoryServer
from app.db.index import get_db
from fastapi import Request,status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.util.user_auth import jwt_decode, CheckAccessTokenData



async def check_token_exist(request: Request):
  access_token = request.cookies.get("access_token")
  if not access_token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token is missing",
    )
  return access_token


async def get_current_user(
  token: Annotated[str, Depends(check_token_exist)],
  db: Annotated[AsyncSession, Depends(get_db)]
):
  user_repo = UserRepositoryServer(db)
  payload = jwt_decode(token)

  token_data = CheckAccessTokenData(**payload, get_user_by_uid=user_repo.get_by_uid, db=db)
  await token_data.validate()


  return token_data.user


