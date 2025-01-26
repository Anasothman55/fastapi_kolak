from app.models import *


class TimestampMixin:
  #created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now()))
  #updated_at: datetime = Field(
  #  sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
  #)
  created_at: datetime = Field(
    sa_column_kwargs={
      "server_default": func.now(),
      "nullable": False
    }
  )
  updated_at: datetime = Field(
    sa_column_kwargs={
      "server_default": func.now(),
      "onupdate": func.now(),
      "nullable": False
    }
  )





class RoleBase(str, Enum):
  user = "user"
  admin = "admin"
  superuser = "superuser"

class UserModel(TimestampMixin,SQLModel, table=True):
  __tablename__ = 'usermodels'

  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )
  username: str = Field(unique=True, index=True)
  email: str = Field(unique=True, index=True)
  first_name: str = Field(index=True)
  last_name: str = Field(index=True)
  role: str = Field(sa_column=Column(SQLEnum(RoleBase), default=RoleBase.user))
  is_active: bool = Field(default=True)
  hash_password: str = Field(exclude=True)
  last_login: datetime = Field(nullable=True)

  def __repr__(self):
    return f"<Book {self.username}>"





class EmployeeModel(TimestampMixin,SQLModel, table=True):
  __tablename__ = 'employeemodels'

  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )
  # ? English name
  first_name : str = Field(index=True)
  middle_name : str = Field(index=True)
  last_name : str = Field(index=True, nullable=True)
  full_name : str = Field(index=True, nullable=True)

  # ? Kurdish name
  first_name_kr : str = Field(index=True)
  middle_name_kr : str = Field(index=True)
  last_name_kr : str = Field(index=True, nullable=True)
  full_name_kr : str = Field(index=True, nullable=True)

  #? Contact information
  email: str = Field(unique=True, index=True, nullable=True)
  phone_number: str = Field(unique=True, index=True, nullable=True)

  #? Address information
  governorate : str = Field(index=True, nullable=True)
  city : str  = Field( index=True, nullable=True )
  neighborhood : str = Field( index=True, nullable=True)

  #? Person information
  date_of_birth : date = Field(sa_column=Column(pg.DATE(), nullable=True))
  nations : str =  Field(default="kurdish")
  gender : str =  Field( nullable=False)

  #? Work information
  job_title : str = Field(nullable=True)
  salary : Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
  hire_date : date = Field(nullable=True)
  fire_date : date = Field(nullable=True)
  is_active : bool = Field(default=True)



  user_uid : uuid.UUID | None = Field(default=None ,foreign_key="usermodels.uid")

  daily_work : Optional[List["EmployeeDailyWork"]] = Relationship(back_populates="employee", sa_relationship_kwargs={"lazy": "selectin"})
  stock_use: Optional[List["UseProductModels"]] = Relationship(back_populates="employee",sa_relationship_kwargs={"lazy": "selectin"})

  def __repr__(self):
    return f"<Employee {self.full_name}>"

@event.listens_for(EmployeeModel, "before_insert")
@event.listens_for(EmployeeModel, "before_update")
def generate_full_names(mapper, connection, target):
  # Generate full_name for English names
  target.full_name = " ".join(
    filter(None, [target.first_name, target.middle_name, target.last_name])
  )
  # Generate full_name_kr for Kurdish names
  target.full_name_kr = " ".join(
    filter(None, [target.first_name_kr, target.middle_name_kr, target.last_name_kr])
  )





class EmployeeDailyWork(TimestampMixin,SQLModel, table=True):
  __tablename__ = 'dailyworkmodels'

  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )

  is_work : bool = False
  start: datetime = Field(default_factory=lambda: datetime.combine(datetime.today(), time(7, 0)), nullable=True)
  end: datetime = Field(default_factory=lambda: datetime.combine(datetime.today(), time(16, 0)), nullable=False)
  work_hours: timedelta = Field(nullable=True)

  emp_uid: uuid.UUID | None  = Field(default=None, foreign_key="employeemodels.uid")
  user_uid : uuid.UUID | None = Field(default=None ,foreign_key="usermodels.uid")

  employee : Optional[EmployeeModel] = Relationship(back_populates="daily_work")

  def __repr__(self):
    return f"<Daily work emp_uid {self.emp_uid}>"


@event.listens_for(EmployeeDailyWork, "before_insert")
@event.listens_for(EmployeeDailyWork, "before_update")
def calculate_duration(mapper, connection, target):
  if not target.is_work:
    target.start = None
    target.end = None
    target.work_hours = None
  elif target.start and target.end:
    target.work_hours = target.end - target.start



class StockModels(TimestampMixin,SQLModel, table=True):
  __tablename__ = 'stockmodels'

  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )

  name: str | None = None
  quantity: int | None = Field(default=0)
  location: str | None = None


  user_uid : uuid.UUID | None = Field(default=None ,foreign_key="usermodels.uid")

  def __repr__(self):
    return f"<Stock product {self.name}>"





class UseProductModels(TimestampMixin,SQLModel, table=True):
  __tablename__ = 'use_product_models'

  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )

  quantity_toke: int | None = Field(None)
  toke_date: datetime | None = Field(default=datetime.now())
  return_date: datetime | None = Field(None)
  return_quantity: int | None = Field(None)
  is_returned: bool = Field(default=False)
  description: str | None = Field(None)

  emp_uid: uuid.UUID = Field(default=None, foreign_key="employeemodels.uid")
  stock_uid: uuid.UUID = Field(default=None, foreign_key="stockmodels.uid")
  user_uid: uuid.UUID | None = Field(default=None, foreign_key="usermodels.uid")

  employee: Optional[EmployeeModel] = Relationship(back_populates="stock_use")

  def __repr__(self):
    return f"<Use Item emp_uid {self.emp_uid}>"


@event.listens_for(UseProductModels, "before_insert")
@event.listens_for(UseProductModels, "before_update")
def ev(mapper, connection, target):
  if not target.return_quantity:
    target.is_returned = False
  elif target.return_quantity:
    target.is_returned = True

