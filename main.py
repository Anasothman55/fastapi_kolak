from unittest import result
from rich import print
from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.db.index import get_db,AsyncSession,close_db_connection,init_db, text
from contextlib import asynccontextmanager
from typing import Annotated
from app.util.user_auth import user_auth_exception
from app.middleware import register_middleware
from app.core.make_admin import create_admin





@asynccontextmanager
async def life_span(app: FastAPI):
  try:
    await init_db()
    admin_create = await create_admin()
    print(f"Admin created: {admin_create}")
    print("Application startup complete")
  except Exception as e:
    print("Error during startup: " + str(e))
    raise
  yield
  try:
    await close_db_connection()
    print("Application shutdown complete")
  except Exception as e:
    print(f"Error closing database connection: {str(e)}")



version = "1.0"


app = FastAPI(
  title="HTS API",
  version=version,
  lifespan=life_span
)



user_auth_exception(app)

@app.get("/helth", status_code= status.HTTP_200_OK)
async def helth(db: Annotated[AsyncSession, Depends(get_db)]):
  try:
    result = await db.execute(text("SELECT 1"))
    await db.commit()
    
    return {
      "status": "healthy",
      "database": "connected",
      "message": "Application is running normally",
      "execute": result
    }
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail=f"Database connection failed: {str(e)}"
    )


@app.exception_handler(500)
async def internal_server_error(request, ext):
  return JSONResponse(
    status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={"detail": "Internal Server Error", "error": str(ext)}
  ) 


register_middleware(app)


from app.router.user_auth import auth_router
from app.router.employee import emp_router
from app.router.stock import stock_router
from app.router.use_item import use_item_route

app.include_router(auth_router, prefix=f"/api/{version}/auth")
app.include_router(emp_router, prefix=f"/api/{version}/employee")
app.include_router(use_item_route, prefix=f"/api/{version}/use-stock")  # added this line to include the route in the main router group.
app.include_router(stock_router, prefix=f"/api/{version}/stock")

"""
alembic
1- alembic init -t async migrations
2- alembic revision --autogenerate -m "fix timestamp"
3- -m "first"-> alembic upgrade d58947e48e76    
"""


if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", port=8000, reload=True)





