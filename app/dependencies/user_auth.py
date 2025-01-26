
from app.service.user_auth import UserRepositoryServer
from app.util.user_auth import jwt_decode, CheckAccessTokenData
from fastapi import status, HTTPException, Depends, Response, Request
from app.service.user_auth import AuthenticationService, TokenService
from app.crud.user_auth import UserAuthCrud
from app.db.index import get_db,AsyncSession
from typing import Annotated
from app.core.config import config



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


def get_token_service() -> TokenService:
  return TokenService(config)
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthenticationService:
  return AuthenticationService(db)


def get_user_auth_crud(
  db: Annotated[AsyncSession, Depends(get_db)],
  response: Response,
  token_service: Annotated[TokenService, Depends(get_token_service)],
  auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> UserAuthCrud:
  return UserAuthCrud(db, response, token_service, auth_service)
