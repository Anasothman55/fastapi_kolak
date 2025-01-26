import uuid
from fastapi import APIRouter, status, Depends, Response, Request, Form,Body, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.employee import EmployeeCrud
from app.db.index import get_db
from app.dependencies.admin import get_admin
from app.dependencies.employee import get_employee_crud
from app.models.model import EmployeeModel
from typing import Annotated, List
from app.schemas.use_item import UseStockItemBase, EmployeeUseStock,UpdateEmployeeUseStock
from app.crud.use_item import UseItemCrud


async def get_use_item_crud(db: AsyncSession = Depends(get_db)) -> UseItemCrud:
  return UseItemCrud(db)


use_item_route = APIRouter(tags=["Use Stock (Admin requires)"],dependencies=[Depends(get_admin)])




@use_item_route.post("/", status_code=status.HTTP_201_CREATED, response_model=UseStockItemBase, response_model_exclude_none=True)
async def create_use_item_route(
    use_item_crud: Annotated[UseItemCrud, Depends(get_use_item_crud)],
    admin: Annotated[EmployeeModel, Depends(get_admin)],
    use_item_data: Annotated[EmployeeUseStock, Body()]
):
  use_item = await use_item_crud.create_use_item_crud(use_item_data, admin.uid)
  return use_item



@use_item_route.get("/", status_code=status.HTTP_200_OK)
async def get_all_use_items_route(
    use_item_crud: Annotated[UseItemCrud, Depends(get_use_item_crud)]
):
  use_items = await use_item_crud.get_all_use_items()
  return use_items



@use_item_route.get("/{use_item_uid}", status_code=status.HTTP_200_OK, response_model=UseStockItemBase)
async def get_one_use_item_route(
    use_item_uid: Annotated[uuid.UUID, Path()],
    use_item_crud: Annotated[UseItemCrud, Depends(get_use_item_crud)]
):
  use_item = await use_item_crud.get_one_use_item_crud(use_item_uid)
  return use_item



@use_item_route.patch("/{use_item_uid}", status_code=status.HTTP_200_OK, response_model=UseStockItemBase)
async def update_use_item_route(
    use_item_uid: Annotated[uuid.UUID, Path()],
    use_item_crud: Annotated[UseItemCrud, Depends(get_use_item_crud)],
    use_item_data: Annotated[UpdateEmployeeUseStock, Body()]
):
  updated_use_item = await use_item_crud.update_use_item_crud(use_item_data, use_item_uid)
  return updated_use_item



@use_item_route.delete("/{use_item_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_use_item_route(
    use_item_uid: Annotated[uuid.UUID, Path()],
    use_item_crud: Annotated[UseItemCrud, Depends(get_use_item_crud)]
):
  await use_item_crud.delete_use_item_crud(use_item_uid)


