from starlette.responses import JSONResponse

from ..models.model import EmployeeModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Any
from sqlmodel import select, desc, asc,and_
import  uuid
from fastapi import  status, HTTPException
from app.util.user_auth import  error_schema, create_access_token,verify_password_utils
from datetime import timedelta


class EmployeesRepositoryServer:
  def __init__(self, db: AsyncSession):
    self.db = db
    self.model = EmployeeModel
  async def _statement(self,  field: str, value: Any):
    statement = select(self.model).where(getattr(self.model, field) == value)
    result = await self.db.execute(statement)
    return result.scalars().first()

  async def get_all_employees(self, order_by: str = 'created_at', job_title: str = None):
    order_column = getattr(self.model, order_by, self.model.created_at)

    if order_by.startswith('-'):
      order_column = desc(order_column)
    else:
      order_column = asc(order_column)

    statement = select(self.model).where(self.model.is_active == True).order_by(order_column)
    if job_title:
      statement = statement.where(self.model.job_title == job_title)

    result = await self.db.execute(statement)
    return result.scalars().all()

  async def get_by_email(self, email: str):
    return await self._statement("email", email)

  async def get_by_uid(self, uid: uuid.UUID):
    return await self._statement("uid", uid)


class EmployeeService:
  def __init__(self,db: AsyncSession):
    self.db = db
    self.emp_repo = EmployeesRepositoryServer(db)

  async def check_unique_data(self,email,full_name_kr,full_name,phone_number):
    errors = {}
    if existing_full_name := await self.emp_repo._statement("full_name", full_name):
      errors['full_name'] = error_schema("full_name", existing_full_name.full_name)

    if existing_full_name_kr := await self.emp_repo._statement("full_name_kr",full_name_kr):
      errors['full_name_kr'] = error_schema("full_name_kr", existing_full_name_kr.full_name_kr)

    if email is not None:
      if existing_user := await self.emp_repo.get_by_email(email):
        errors['email'] = error_schema("email", existing_user.email)

    if existing_phone_number := await self.emp_repo._statement("phone_number",phone_number):
      errors['phone_number'] = error_schema("phone_number", existing_phone_number.phone_number)

    return errors

  async def get_one_emp_service(self, emp_uid: uuid.UUID):
    emp =  await self.emp_repo.get_by_uid(emp_uid)

    if not emp:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Employee not found"
      )
    return emp

