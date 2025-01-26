import uuid

from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model import UseProductModels,EmployeeModel, StockModels
from app.schemas.use_item import EmployeeUseStock, UpdateEmployeeUseStock
from rich import  print




class UseItemCrud:
  def __init__(self, db: AsyncSession):
    self.db = db

  async def create_use_item_crud(self, use_item_data: EmployeeUseStock, admin_uid: uuid.UUID):
    emp = query = select(EmployeeModel).where(EmployeeModel.uid == use_item_data.emp_uid)
    result = await self.db.execute(query)

    if not result:
      raise HTTPException(
        status_code=404,
        detail="Employee not found"
      )

    stock = query = select(StockModels).where(StockModels.uid == use_item_data.stock_uid)
    result = await self.db.execute(query)

    if not result:
      raise HTTPException(
        status_code=404,
        detail="Stock not found"
      )

    if result.scalars().first().quantity < use_item_data.quantity_toke:
      raise HTTPException(
        status_code=400,
        detail="Insufficient quantity in stock"
      )

    db_use_item = UseProductModels(
      **use_item_data.model_dump(),
      user_uid=admin_uid
    )
    print(db_use_item)
    self.db.add(db_use_item)
    await self.db.commit()
    await self.db.refresh(db_use_item)
    return db_use_item

  async def get_all_use_items(self):
    query = select(UseProductModels)
    result = await self.db.execute(query)
    return result.scalars().all()

  async def get_one_use_item_crud(self, use_item_uid: uuid.UUID):
    query = select(UseProductModels).where(UseProductModels.uid == use_item_uid)
    result = await self.db.execute(query)
    return result.scalar_one_or_none()

  async def update_use_item_crud(self, use_item_data: UpdateEmployeeUseStock, use_item_uid: uuid.UUID):
    query = select(UseProductModels).where(UseProductModels.uid == use_item_uid)
    result = await self.db.execute(query)
    db_use_item = result.scalar_one_or_none()

    if db_use_item:
      # Update fields that are not None
      update_data = use_item_data.model_dump(exclude_unset=True)
      for key, value in update_data.items():
        setattr(db_use_item, key, value)

      await self.db.commit()
      await self.db.refresh(db_use_item)

    return db_use_item

  async def delete_use_item_crud(self, use_item_uid: uuid.UUID):
    query = select(UseProductModels).where(UseProductModels.uid == use_item_uid)
    result = await self.db.execute(query)
    db_use_item = result.scalar_one_or_none()

    if db_use_item:
      await self.db.delete(db_use_item)
      await self.db.commit()






