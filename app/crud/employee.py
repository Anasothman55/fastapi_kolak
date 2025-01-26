import uuid
from fastapi.responses import JSONResponse
from ..models.model import EmployeeModel
from ..service.employee import EmployeeService
from ..db.index import AsyncSession
from fastapi import status, Response
from ..util.user_auth import ValidationErrorWithUnique
from app.schemas.employee import EmployeeCreate
from app.schemas.use_item import EmployeeUseStock, UseStockItemBase



class EmployeeCrud:
  def __init__(self, db: AsyncSession, response: Response, employee_service: EmployeeService):
    self.db = db
    self.response = response
    self.employee_service = employee_service

  async def get_all_emp(self, order_by: str = 'created_at', job_title: str = None):
    emp = await self.employee_service.emp_repo.get_all_employees(order_by, job_title)
    if not emp:
      return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "No employee found"}
      )
    return emp

  async def create_emp_crud(self, create_emp: EmployeeCreate, admin_uid: uuid.UUID):
    try:
      full_name = " ".join(filter(None, [create_emp.first_name, create_emp.middle_name, create_emp.last_name]))
      full_name_kr = " ".join(filter(None, [create_emp.first_name_kr, create_emp.middle_name_kr, create_emp.last_name_kr]))
      unique_check = {
        "full_name": full_name,
        "full_name_kr": full_name_kr,
        "email": create_emp.email,
        "phone_number": create_emp.phone_number,
      }

      unique_data = await self.employee_service.check_unique_data(**unique_check)
      print(unique_data)
      if unique_data:
        raise ValidationErrorWithUnique(unique_errors=unique_data)


      new_emp = EmployeeModel(
        **create_emp.model_dump(),
        full_name_kr=full_name_kr,
        full_name=full_name,
        user_uid=admin_uid,
      )

      self.db.add(new_emp)
      await self.db.commit()

      return new_emp
    except ValidationErrorWithUnique as e:
      raise e

  async def update_emp_crud(self, update_emp: EmployeeCreate, emp_uid: uuid.UUID):
    emp = await self.employee_service.get_one_emp_service(emp_uid)
    try:
      # Unique data check
      unique_check = {
        "full_name": " ".join(filter(None, [update_emp.first_name, update_emp.middle_name, update_emp.last_name])),
        "full_name_kr": " ".join(filter(None, [update_emp.first_name_kr, update_emp.middle_name_kr, update_emp.last_name_kr])),
        "email": update_emp.email or emp.email,
        "phone_number": update_emp.phone_number or emp.phone_number,
      }

      unique_data = await self.employee_service.check_unique_data(**unique_check)

      if unique_data:
        raise ValidationErrorWithUnique(unique_errors=unique_data)


      for k, v in update_emp.model_dump(exclude_unset=True).items():
        if v:
          setattr(emp, k, v)

      await self.db.commit()
      await self.db.refresh(emp)

      return emp
    except ValidationErrorWithUnique as e:
      raise e

  async def get_one_emp_crud(self, emp_uid: uuid.UUID):
    return await self.employee_service.get_one_emp_service(emp_uid)

  async def delete_emp_crud(self, emp_uid: uuid.UUID):
    emp = await self.employee_service.get_one_emp_service(emp_uid)

    await self.db.delete(emp)
    await self.db.commit()

    return None
