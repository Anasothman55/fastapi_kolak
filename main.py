from unittest import result
from rich import print
from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.db.index import get_db,AsyncSession,close_db_connection,init_db, text
from contextlib import asynccontextmanager
from typing import Annotated
from app.router.user_auth import auth_router
from app.util.user_auth import register_all_errors
from app.middleware import register_middleware



@asynccontextmanager
async def life_span(app: FastAPI):
  try:
    await init_db()
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

register_all_errors(app)

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

app.include_router(auth_router, prefix=f"/{version}/auth")


"""
alembic
1- alembic init -t async migrations
2-  alembic revision --autogenerate -m "remove is_verify"
3- alembic upgrade a42a831f8a84    
"""


if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", port=8000, reload=True)





