import uuid

from passlib.context import CryptContext
from typing import Dict, Any, Callable, Optional
from fastapi import FastAPI, status, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import timedelta,datetime,timezone

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from jose import jwt, JWTError
from dataclasses import  dataclass

from app.models.user import UserModel




#? Password hashing and password verification
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password_utils(password: str) ->str:
  return pwd.hash(password)

def verify_password_utils(plain_password: str, hash_password: str)-> bool:
  return pwd.verify(plain_password, hash_password)



#? Error and validation part
def error_schema(body: str, field: str):
  return {
    "type": "conflict",
    "loc": ["body", body],
    "msg": "Username already exists",
    "input": {body: field}
  }

class ValidationErrorWithUnique(Exception):
  def __init__(self, pydantic_errors: list = None, unique_errors: Dict = None):
    self.pydantic_errors = pydantic_errors or []
    self.unique_errors = unique_errors or {}

async def validation_exception_handler(request: Request, exc: ValidationErrorWithUnique):
  error_details = []
  if exc.pydantic_errors:
    error_details.extend(exc.pydantic_errors)
  if exc.unique_errors:
    for field, error in exc.unique_errors.items():
      if isinstance(error, dict):
        error_details.append(error)
      else:
        error_details.append(error_schema(field, str(error)))
  return JSONResponse(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    content={"detail": error_details}
  )


def register_all_errors(app: FastAPI):
  app.add_exception_handler(
    ValidationErrorWithUnique,
    validation_exception_handler
  )



def create_access_token(data:dict,expires_delta: timedelta | None = None, refresh: bool = False):
  to_encod = data.copy()
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
  to_encod.update({"exp": expire})
  to_encod.update({"refresh": refresh})

  encoded_jwt = jwt.encode(to_encod, config.SECRET_KEY, algorithm=config.ALGORITHM)
  return encoded_jwt


def jwt_decode(token: str, options: dict | None = None):
  try:
    if options:
      payload = jwt.decode(token, config.SECRET_KEY,algorithms= config.ALGORITHM, options=options)
    else:
      payload = jwt.decode(token, config.SECRET_KEY, algorithms=config.ALGORITHM)
    return payload
  except JWTError as jex:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'error': str(jex), 'message': "Invalid"})


@dataclass
class CheckAccessTokenData:
  sub: str
  email: EmailStr
  jit: str
  fid: str
  exp: int
  refresh: bool
  user: UserModel | None = None
  get_user_by_uid: Callable[[uuid.UUID], Optional[UserModel]] = None
  db: AsyncSession = None
  async def validate(self):
    credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
    )

    if not all([self.sub, self.email, self.jit, self.fid, self.exp]):
      raise credentials_exception

    user_data = await self.get_user_by_uid(uuid.UUID(self.sub))

    if not user_data:
      raise credentials_exception

    self.user = user_data

    if not self.user.is_active:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is inactive. Please contact support.",
      )










