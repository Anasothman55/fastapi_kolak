
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, EmailStr, StrictStr, field_validator
import uuid
from enum import Enum
import uuid
from decimal import Decimal
from typing import Optional,List
from app.schemas.daily_work import DailyWorkBase
from app.schemas.use_item import UseStockItemBase



class GenderEnum(str,Enum):
  male = "male"
  female = "female"

class JobTitleEnum(str,Enum):
  manager = "manager"
  supervisor = "supervisor"
  worker = "worker"
  driver = "driver"
  surveyor = "surveyor"
  cleaner = "cleaner"
  gard = "gard"
  sales = "sales"
  lower = "lower"
  manager_assistant = "manager_assistant"
  machine_kipper = "machine_operator"
  worker_kipper = "worker_kipper"
  it = "it"
  engineer = "engineer"
  accountant_manager = "accountant_manager"


class EmployeeSortEnum(str,Enum):
  full_name = "full_name"
  full_name_kr = "full_name_kr"
  email = "email"
  phone_number = "phone_number"
  governorate = "governorate"
  city = "city"
  neighborhood = "neighborhood"
  hire_date = "hire_date"
  updated_at = "updated_at"
  created_at = "created_at"

  def to_str(self):
    return self.value


class EmployeeSortEnum2(str,Enum):
  full_name = "full_name"
  full_name_kr = "full_name_kr"

  def to_str(self):
    return self.value


class EmployeeBase(BaseModel):
  first_name: str = Field(pattern=r"^[A-Za-z]+$")
  middle_name: str = Field(pattern=r"^[A-Za-z]+$")
  last_name: str | None  = Field(None , pattern=r"^[A-Za-z]+$")
  #r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+$" this code ensure that the name is in arabic and persian and kurdish letter only
  first_name_kr: str = Field(pattern=r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+$")
  middle_name_kr: str = Field(pattern=r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+$")
  last_name_kr: str | None = Field(None , pattern=r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+$")

  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "first_name": "John",
        "middle_name": "Doe",
        "last_name": "Smith",
        "first_name_kr": "جون",
        "middle_name_kr": "دو",
        "last_name_kr": "سمیث"
      }
    }
  )

class UpdateEmployee(BaseModel):
  full_name_kr: str
  full_name: str

class EmployeeCreate(EmployeeBase):
  email: EmailStr | None = Field(None)
  phone_number: str = Field( pattern= r"^\d{4}\s?\d{3}\s?\d{4}$")

  governorate: str | None = Field(None)
  city: str | None = Field(None)
  neighborhood: str | None = Field(None)

  date_of_birth: date | None = Field(None)
  nations: str | None  = Field(default="Kurdish")
  gender: GenderEnum = Field(default=GenderEnum.male)

  job_title: JobTitleEnum = Field(default=JobTitleEnum.worker)
  salary: Decimal | None = Field(None)
  hire_date: date | None = Field(None)

  @field_validator("email", "salary", mode="before")
  def convert_empty_string_to_none(cls, v):
    if v == "":
      return None
    return v

  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "first_name": "John",
        "middle_name": "Doe",
        "last_name": "Smith",

        "first_name_kr": "جون",
        "middle_name_kr": "دو",
        "last_name_kr": "سمیث",

        "email": "john.smith@example.com",
        "phone_number": "1234 567 8901",

        "governorate": "Baghdad",
        "city": "Baghdad",
        "neighborhood": "Al-Mansour",

        "date_of_birth": "1985-07-15",
        "nations": "Iraqi",
        "gender": "male",

        "job_title": "manager",
        "salary": 1500.50,
        "hire_date": "2020-05-10",
      }
    }
  )



class EmployeeOut(BaseModel):
  uid: uuid.UUID
  is_active: bool
  full_name: str
  phone_number: str
  hire_date: date



class EmployeeFullOut(EmployeeCreate):
  fire_date: date | None
  is_active: bool
  full_name_kr: str | None = None
  uid: uuid.UUID
  full_name: str | None = None

  created_at: datetime
  updated_at: datetime




class EmployeeDailyWorkFullOut(EmployeeFullOut):
  daily_work: List[DailyWorkBase] = []
  stock_use: List[UseStockItemBase] = []







