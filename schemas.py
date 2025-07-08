import pydantic #convierte la data entre los models y los schemas
import datetime as datetime


class UserBase(pydantic.BaseModel):
    email: str
    name: str
    phone: str


class UserRequest(UserBase):
    password: str

    class Config: #Le permite a Pydantic aceptar instancias de objetos ORM (como SQLAlchemy), 
        #Para que .from_orm() funcione y FastAPI pueda convertir modelos de DB
        orm_mode = True


class UserResponse(UserBase):
    id: int
    created_at: datetime.datetime

    class Config: 
        orm_mode = True


class PostBase(pydantic.BaseModel):
    post_title: str
    post_description: str
    image: str

class PostRequest(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    class Config: 
        orm_mode = True