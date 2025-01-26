from datetime import datetime
from pydantic import BaseModel, Field
import uuid
from enum import Enum



class StockSortEnum(str,Enum):
  quantity = "quantity"
  name = "name"
  updated_at = "updated_at"
  created_at = "created_at"

  def to_str(self):
    return self.value


class BaseStock(BaseModel):
  name : str | None = Field(None)
  quantity: int | None = Field(default=0)
  location: str | None = None


class StockOut(BaseStock):
  uid: uuid.UUID
  created_at: datetime
  updated_at: datetime

  user_uid: uuid.UUID | None = None








