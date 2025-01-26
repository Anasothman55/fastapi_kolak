
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field, ConfigDict, EmailStr, StrictStr, field_validator
import uuid
from enum import Enum
import uuid
from decimal import Decimal
from typing import Optional,List






class DailyWorkBase(BaseModel):
  uid: uuid.UUID
  is_work : bool
  start: datetime
  end: datetime
  work_hours: timedelta | None = Field(None)

  created_at: datetime
  updated_at: datetime
