
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field, ConfigDict, EmailStr, StrictStr, field_validator
import uuid
from enum import Enum
import uuid
from decimal import Decimal
from typing import Optional,List




class EmployeeUseStock(BaseModel):
  stock_uid: uuid.UUID
  emp_uid: uuid.UUID| None = None
  quantity_toke: int  = Field(gt=0)
  toke: datetime | None = None
  description: str| None = None

  model_config = ConfigDict(
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="forbid",

    json_schema_extra={
      "example": {
        "item_uid": uuid.uuid4(),
        "emp_uid": uuid.uuid4(),
        "qty": 10,
        "toke": datetime.now(),
        "description": "used for employee"
      }
    }
  )


class UpdateEmployeeUseStock(BaseModel):
  item_uid: uuid.UUID| None = None
  emp_uid: uuid.UUID | None = None
  qty: int| None = None
  toke: datetime | None = None
  description: str | None = None

  model_config = ConfigDict(
    validate_assignment=True,
    str_strip_whitespace=True,
    extra="forbid",

    json_schema_extra={
      "example": {
        "item_uid": uuid.uuid4(),
        "emp_uid": uuid.uuid4(),
        "qty": 10,
        "toke": datetime.now(),
        "description": "used for employee"
      }
    }
  )


class UseStockItemBase(BaseModel):

  uid: uuid.UUID
  quantity_toke: int | None = Field(None)
  toke_date: datetime | None =  None
  return_date: datetime | None = Field(None)
  return_quantity: int | None = Field(None)
  is_returned: bool = Field(default=False)
  description: str | None = Field(None)

  created_at: datetime
  updated_at: datetime

  stock_uid: uuid.UUID | None = Field(default=None)
