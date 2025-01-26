
from sqlmodel import select
from app.models.model import UserModel
from app.schemas.user_auth import CreateUser
from rich import print
from app.db.index import get_db
from app.util.user_auth import hash_password_utils
from  datetime import datetime


async def create_admin():
  try:
    db = await anext(get_db())
    register_model = CreateUser(
      email="anasothmanadmin@gmail.com",
      password="admin123",
      username="admin",
      first_name="Admin",
      last_name="User",
    )

    statement = select(UserModel).where(getattr(UserModel, "username") == "admin")
    result = await db.execute(statement)
    user_exist = result.scalars().first()

    if user_exist:
      return {
        'msg': "admin already exist",
        "admin": user_exist.uid
      }

    hashing = hash_password_utils(register_model.password)
    user_data = register_model.model_dump(exclude={"password"})
    new_user = UserModel(**user_data, hash_password=hashing)
    new_user.last_login = datetime.now()
    new_user.role = "admin"
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
  except Exception as e:
    print("Error creating admin user:", str(e))
    raise
