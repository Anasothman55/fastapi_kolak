import uuid

from fastapi import APIRouter, status, Depends, Response, Request, Form,Body, Query, Path
from app.crud.employee import EmployeeCrud
from app.dependencies.admin import get_admin
from app.dependencies.employee import get_employee_crud
from app.models.model import EmployeeModel
from typing import Annotated, List
from app.schemas.employee import EmployeeOut,EmployeeCreate, EmployeeFullOut, EmployeeSortEnum,JobTitleEnum, EmployeeDailyWorkFullOut
from app.schemas.use_item import EmployeeUseStock

emp_router = APIRouter(tags=["Employee (Admin requires)"], dependencies=[Depends(get_admin)])




#? Employee Routes --------------------------------

@emp_router.get("/", status_code=status.HTTP_200_OK, response_model=List[EmployeeFullOut])
async def get_all_employees_route(
    *,
    emp_crud: Annotated[EmployeeCrud, Depends(get_employee_crud)],
    order_by: Annotated[EmployeeSortEnum, Query()] = EmployeeSortEnum.created_at,
    job_title: Annotated[JobTitleEnum, Query()] | None = None,
    descending: Annotated[bool, Query()] = False
):

  order_by = order_by.to_str().lower()
  if descending:
    order_by = f"-{order_by}"
  employee = await emp_crud.get_all_emp(order_by, job_title)
  return employee


@emp_router.post("/create-employee", status_code=status.HTTP_201_CREATED, response_model=EmployeeOut , response_model_exclude_none= True)
async def create_employee_route(
    emp_crud: Annotated[EmployeeCrud, Depends(get_employee_crud)],
    admin: Annotated[EmployeeModel, Depends(get_admin)],
    emp_data: Annotated[EmployeeCreate, Form()]):
  employee = await emp_crud.create_emp_crud(emp_data,admin.uid)
  return employee


@emp_router.delete("/delete-emp/{emp_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee_route(
    emp_uid: Annotated[uuid.UUID, Path()],emp_crud: Annotated[EmployeeCrud, Depends(get_employee_crud)]):
  await emp_crud.delete_emp_crud(emp_uid)



@emp_router.patch("/update-employee/{emp_uid}", status_code=status.HTTP_201_CREATED, response_model=EmployeeOut , response_model_exclude_none= True)
async def update_employee_route(
    emp_crud: Annotated[EmployeeCrud, Depends(get_employee_crud)],
    emp_uid: Annotated[uuid.UUID, Path()],
    emp_data: Annotated[EmployeeCreate, Body()]):
  employee = await emp_crud.update_emp_crud(emp_data,emp_uid)
  return employee




@emp_router.get("/{emp_uid}", status_code=status.HTTP_200_OK, response_model=EmployeeDailyWorkFullOut, response_model_exclude_unset=True)
async def get_one_employees_route(
    emp_crud: Annotated[EmployeeCrud, Depends(get_employee_crud)],
    emp_uid: Annotated[uuid.UUID, Path()]
):

  employee = await emp_crud.get_one_emp_crud(emp_uid)
  return employee








