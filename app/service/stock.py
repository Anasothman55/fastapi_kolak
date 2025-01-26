from starlette.responses import JSONResponse

from ..models.model import StockModels
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Any
from sqlmodel import select, desc, asc,and_
import  uuid
from fastapi import  status, HTTPException
from app.util.user_auth import  error_schema, create_access_token,verify_password_utils
from datetime import timedelta


class StockRepositoryServer:
  def __init__(self, db: AsyncSession):
    self.db = db
    self.model = StockModels
  async def _statement(self,  field: str, value: Any):
    statement = select(self.model).where(getattr(self.model, field) == value)
    result = await self.db.execute(statement)
    return result.scalars().first()

  async def get_all_stock(self, order_by: str = 'created_at'):
    order_column = getattr(self.model, order_by, self.model.created_at)

    if order_by.startswith('-'):
      order_column = desc(order_column)
    else:
      order_column = asc(order_column)

    statement = select(self.model).order_by(order_column)
    result = await self.db.execute(statement)
    return result.scalars().all()

  async def get_by_name(self, email: str):
    return await self._statement("email", email)

  async def get_by_uid(self, uid: uuid.UUID):
    return await self._statement("uid", uid)


class StockService:
  def __init__(self,db: AsyncSession):
    self.db = db
    self.stock_repo = StockRepositoryServer(db)

  async def check_unique_data(self,name : str):
    errors = {}
    if existing_name := await self.stock_repo._statement("name", name):
      errors['name'] = error_schema("name", existing_name.name)

    return errors

  async def get_one_item_service(self, item_uid: uuid.UUID):
    item =  await self.stock_repo.get_by_uid(item_uid)

    if not item:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Item not found"
      )
    return item

