from fastapi.params import Depends
from fastapi import HTTPException, status
from sqlalchemy.sql.annotation import Annotated
from .user_auth import get_current_user
from app.models.model import UserModel


async def get_admin(current_user: UserModel = Depends(get_current_user)):
  if not current_user.role == "admin":
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
  return current_user