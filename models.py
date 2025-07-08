from datetime import datetime, timezone
import sqlalchemy as sqlalchemy
import sqlalchemy.orm as orm
import passlib.hash as hash

import database as database
from database import Base


class UserModel(Base):
    __tablename__ = "users" #se define el nombre de la tabla (asi es en sqlalchemy), a continuacion los campos
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index= True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index= True)
    name = sqlalchemy.Column(sqlalchemy.String)
    phone = sqlalchemy.Column(sqlalchemy.String)
    password_hash = sqlalchemy.Column(sqlalchemy.String)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now(timezone.utc))
    posts = orm.relationship("PostModel", back_populates="user") #relacion que va a tener con posts, se tiene que crear una relacion igual en posts, 
    #cuando post intente llenarse va a recurrir al campo con la relacion en el model de post (del campo user, el que se pone en back_populates, 
    # tiene que ser como está definido en post)

    #metodo para verificar password
    def password_verification(self, password: str):
        return hash.bcrypt.verify(password, self.password_hash) #las pass va a estar hash, entonces por eso se usa el metodo para comprobarla




class PostModel(Base):
    __tablename__ = "posts"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index= True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")) #foreging key relation with users table
    post_title = sqlalchemy.Column(sqlalchemy.String, index= True)
    post_description = sqlalchemy.Column(sqlalchemy.String, index= True)
    image = sqlalchemy.Column(sqlalchemy.String)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now(timezone.utc))
    user = orm.relationship("UserModel", back_populates="posts") 