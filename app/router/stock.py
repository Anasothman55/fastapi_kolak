import uuid

from fastapi import APIRouter, status, Depends, Response, Request, Form,Body, Query, Path
from app.crud.stock import StockCrud
from app.dependencies.admin import get_admin
from app.dependencies.stock import get_stock_crud
from app.models.model import StockModels, EmployeeModel
from typing import Annotated, List
from app.schemas.stock import BaseStock, StockOut, StockSortEnum



stock_router = APIRouter(tags=["Stock (Admin requires)"], dependencies=[Depends(get_admin)])


@stock_router.get("/", status_code=status.HTTP_200_OK, response_model=List[StockOut])
async def get_all_stock_route(
    *,
    stock_crud: Annotated[StockCrud, Depends(get_stock_crud)],
    order_by: Annotated[StockSortEnum, Query()] = StockSortEnum.created_at,
    descending: Annotated[bool, Query()] = False
):

  order_by = order_by.to_str().lower()
  if descending:
    order_by = f"-{order_by}"
  stock = await stock_crud.get_all_item(order_by)
  return stock


@stock_router.post("/create-employee", status_code=status.HTTP_201_CREATED, response_model=StockOut , response_model_exclude_none= True)
async def create_stock_route(
    stock_crud: Annotated[StockCrud, Depends(get_stock_crud)],
    admin: Annotated[EmployeeModel, Depends(get_admin)],
    stock_data: Annotated[BaseStock, Form()]):
  stock = await stock_crud.create_stock_crud(stock_data,admin.uid)
  return stock


@stock_router.delete("/delete-emp/{item_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock_route(
    item_uid: Annotated[uuid.UUID, Path()],stock_crud: Annotated[StockCrud, Depends(get_stock_crud)]):
  await stock_crud.delete_stock_crud(item_uid)



@stock_router.patch("/update-employee/{item_uid}", status_code=status.HTTP_201_CREATED, response_model=StockOut , response_model_exclude_none= True)
async def update_stock_route(
    stock_crud: Annotated[StockCrud, Depends(get_stock_crud)],
    item_uid: Annotated[uuid.UUID, Path()],
    stock_data: Annotated[BaseStock, Body()]):
  stock = await stock_crud.update_stock_crud(stock_data,item_uid)
  return stock



@stock_router.get("/{item_uid}", status_code=status.HTTP_200_OK, response_model=StockOut, response_model_exclude_unset=True)
async def get_one_stock_route(
    stock_crud: Annotated[StockCrud, Depends(get_stock_crud)],
    item_uid: Annotated[uuid.UUID, Path()]
):

  stock = await stock_crud.get_one_item_crud(item_uid)
  return stock





