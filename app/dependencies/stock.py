from app.crud.stock import StockCrud
from fastapi import status, HTTPException, Depends, Response, Request
from app.db.index import get_db,AsyncSession
from typing import Annotated
from app.service.stock import StockService



def get_stock_service(db: AsyncSession = Depends(get_db)) -> StockService:
  return StockService(db)



def get_stock_crud(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    stock_service: Annotated[StockService, Depends(get_stock_service)]
) -> StockCrud:
  return StockCrud(db, response,stock_service)
