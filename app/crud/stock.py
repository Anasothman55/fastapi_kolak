import uuid
from fastapi.responses import JSONResponse
from ..models.model import StockModels
from ..service.stock import StockService
from ..db.index import AsyncSession
from fastapi import status, Response
from ..util.user_auth import ValidationErrorWithUnique
from app.schemas.stock import BaseStock
from rich import print



class StockCrud:
  def __init__(self, db: AsyncSession, response: Response, stock_service: StockService):
    self.db = db
    self.response = response
    self.stock_service = stock_service

  async def get_all_item(self, order_by: str = 'created_at'):
    item = await self.stock_service.stock_repo.get_all_stock(order_by)
    if not item:
      return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "No item found in stock"}
      )
    return item

  async def create_stock_crud(self, create_stock: BaseStock, admin_uid: uuid.UUID):
    try:
      unique_data = await self.stock_service.check_unique_data(create_stock.name)

      if unique_data:
        raise ValidationErrorWithUnique(unique_errors=unique_data)

      new_stock = StockModels(
        **create_stock.model_dump(),
        user_uid=admin_uid,
      )

      self.db.add(new_stock)
      await self.db.commit()

      return new_stock
    except ValidationErrorWithUnique as e:
      raise e

  async def update_stock_crud(self, update_stock: BaseStock, item_uid: uuid.UUID):
    item = await self.stock_service.get_one_item_service(item_uid)
    try:
      unique_data = await self.stock_service.check_unique_data(update_stock.name)
      if unique_data:
        raise ValidationErrorWithUnique(unique_errors=unique_data)

      for k, v in update_stock.model_dump(exclude_unset=True).items():
        if v:
          setattr(item, k, v)

      await self.db.commit()
      await self.db.refresh(item)

      return item
    except ValidationErrorWithUnique as e:
      raise e

  async def get_one_item_crud(self, item_uid: uuid.UUID):
    return await self.stock_service.get_one_item_service(item_uid)

  async def delete_stock_crud(self, item_uid: uuid.UUID):
    item = await self.stock_service.get_one_item_service(item_uid)

    await self.db.delete(item)
    await self.db.commit()

    return None
