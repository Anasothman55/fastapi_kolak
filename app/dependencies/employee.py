from app.crud.employee import EmployeeCrud
from fastapi import status, HTTPException, Depends, Response, Request
from app.db.index import get_db,AsyncSession
from typing import Annotated
from app.service.employee import EmployeeService



def get_emp_service(db: AsyncSession = Depends(get_db)) -> EmployeeService:
  return EmployeeService(db)



def get_employee_crud(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    employee_service: Annotated[EmployeeService, Depends(get_emp_service)]
) -> EmployeeCrud:
  return EmployeeCrud(db, response,employee_service)
