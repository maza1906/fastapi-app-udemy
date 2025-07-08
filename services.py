import database as database
import models
import sqlalchemy.orm as orm
import schemas
import email_validator
import fastapi
import passlib.hash as hash
import jwt
import fastapi.security as security

jwt_secret = "abcabc" #esto debe estar seguro y no aqui, en una env variable, esta es para ejemplo
oauth2schema = security.OAuth2PasswordBearer("/api/v1/login")

#metodo para crear db
def create_db():
    return database.Base.metadata.create_all(bind=database.engine)

#funcion para obtener la sesion
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

#funcion que escribe un query, y checa la db por el email
async def getUserByEmail(email: str, db: orm.Session):
    return db.query(models.UserModel).filter(models.UserModel.email == email).first()        

async def create_user(user: schemas.UserRequest, db=orm.Session):
    #esta funcion va a transformar un UserRequest en un UserModel, algo que viene de la API a que hable con la db
    #validar email
    try:
        isValid = email_validator.validate_email(user.email)
        email = isValid.email
    except email_validator.EmailNotValidError:
        raise fastapi.HTTPException(status_code=400, detail="Email is not valid")
    
    #convierte pass en una hashed
    hashed_password = hash.bcrypt.hash(user.password)
    #crea el user model para que se guarde en la db
    user_object = models.UserModel(
        email=email,
        name=user.name,
        phone=user.phone,
        password_hash=hashed_password

    )

    #guardar user en la db
    db.add(user_object)
    db.commit()
    db.refresh(user_object)

    return user_object

async def create_token(user: models.UserModel):
    #convertir UserModel en user schema
    user_schema = schemas.UserResponse.model_validate(user, from_attributes=True)
    #convertir a un dict
    user_dict = user_schema.model_dump()

    del user_dict["created_at"] #eliminar del dict el created_at
    print(user_dict)

    token = jwt.encode(user_dict, jwt_secret)

    return dict(access_token=token, token_type="bearer")

async def login(email: str, password: str, db: orm.Session):
    db_user = await getUserByEmail(email=email, db=db)
    #get user devuelve un objeto del tipo UserModel, que va a tener el método de verificar la pass
    if not db_user:
        return False
    
    if not db_user.password_verification(password=password):
        return False
    
    return db_user

async def current_user(db: orm.Session = fastapi.Depends(get_db), token: str = fastapi.Depends(oauth2schema)): #el depends significa que depende del token que el endpoint the login nos devuelve
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        #get user by id, id is in the decoded user payload, along with email, phone, name
        db_user = db.query(models.UserModel).get(payload["id"])

    except:
        raise fastapi.HTTPException(status_code=401, detail="Wrong credentials")
    
     #convertir UserModel en user schema
    return schemas.UserResponse.model_validate(db_user, from_attributes=True)

async def create_post(user: schemas.UserResponse, db: orm.Session, post: schemas.PostRequest):
    post_data = post.model_dump()          # convierte el esquema a dict
    post = models.PostModel(**post_data, user_id=user.id)#"Pasa cada clave-valor del diccionario post_data como argumento nombrado a PostModel, además de user_id=user.id."
    db.add(post)
    db.commit()
    db.refresh(post)

    return schemas.PostResponse.model_validate(post, from_attributes=True)

async def get_posts_by_user(user: schemas.UserResponse, db: orm.Session):
    posts = db.query(models.PostModel).filter_by(user_id=user.id)
    #convert post model to post schema and make a list to be returned
    return [schemas.PostResponse.model_validate(post, from_attributes=True) for post in posts]

async def get_posts_by_all( db: orm.Session):
    posts = db.query(models.PostModel)
    #convert post model to post schema and make a list to be returned
    return [schemas.PostResponse.model_validate(post, from_attributes=True) for post in posts]

async def get_post_detail(post_id: int, db: orm.Session):
    #get post from db
    db_post = db.query(models.PostModel).filter(models.PostModel.id==post_id).first()
    if db_post is None:
        raise fastapi.HTTPException(status_code=404, detail="Post not found")

    #convert it to a response model
    #return schemas.PostResponse.model_validate(db_post, from_attributes=True) #schema type of information
    return db_post #changed it to make the endpoint for delete work

async def get_user_detail(user_id: int, db: orm.Session):

    db_user = db.query(models.UserModel).filter(models.UserModel.id==user_id).first()
    if db_user is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    #convert it to a response model
    return schemas.UserResponse.model_validate(db_user, from_attributes=True) #schema type of information

async def delete_post(post: models.PostModel, db: orm.Session):
    db.delete(post)
    db.commit()

async def update_post(post_request: schemas.PostRequest, post: models.PostModel, db: orm.Session):
    post.post_title = post_request.post_title
    post.post_description = post_request.post_description
    post.image = post_request.image

    db.commit()
    db.refresh(post)

    return schemas.PostResponse.model_validate(post, from_attributes=True)