import fastapi 
import fastapi.security as security
import sqlalchemy.orm as orm
import schemas
import services
from typing import List

from fastapi.middleware.cors import CORSMiddleware #para evitar cors error

app = fastapi.FastAPI() #esta va a triggerear nuestra app de fastapi

# para evitar cors error
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["url1", "url2"]
    allow_origins = ["*"], #permite todos los url accedan a la app
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.post("/api/v1/users")
async def register_user(
    user: schemas.UserRequest, 
    db: orm.Session = fastapi.Depends(services.get_db)
):
    #revisar si existe el user con el email
    db_user = await services.getUserByEmail(email=user.email, db=db) #await pq como es una async function, hay que esperar a que resuelva para seguir
    if db_user:
        raise fastapi.HTTPException(status_code=400, detail="Email already exists")
    
    #crear el user y regresar el token
    db_user = await services.create_user(user=user, db=db)
    return await services.create_token(user=db_user)

#endpoint para login
@app.post("/api/v1/login")
async def login_user(
        form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
        db: orm.Session = fastapi.Depends(services.get_db)
):
    db_user = await services.login(email=form_data.username, password=form_data.password, db=db)
    #si el login es invalid lanzar exception
    if not db_user:
        raise fastapi.HTTPException(status_code=401, detail= "Wrong login credentials")
    #create and return token
    return await services.create_token(db_user)

@app.get("/api/v1/users/current-user", response_model=schemas.UserResponse)
async def current_user(
    user: schemas.UserResponse = fastapi.Depends(services.current_user)
):
    return user

@app.post("/api/v1/posts", response_model=schemas.PostResponse)
async def create_post(
    post_request: schemas.PostRequest,
    user: schemas.UserRequest = fastapi.Depends(services.current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    
    return await services.create_post(user=user, db=db, post=post_request)

@app.get("/api/v1/posts/user", response_model=List[schemas.PostResponse])
async def get_posts_by_user(
    user: schemas.UserRequest = fastapi.Depends(services.current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_posts_by_user(user=user, db=db)

@app.get("/api/v1/posts/all", response_model=List[schemas.PostResponse])
async def get_posts_by_all(
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_posts_by_all(db=db)

#cualquiera puede acceder a este endpoint, no se necesita autenticacion
@app.get("/api/v1/posts/{post_id}/", response_model=schemas.PostResponse)
async def get_post_detail(
    post_id: int,
    db: orm.Session = fastapi.Depends(services.get_db)
):
    post = await services.get_post_detail(post_id=post_id, db=db)
    
    return post

@app.get("/api/v1/users/{user_id}/", response_model=schemas.UserResponse)
async def get_user_detail(
    user_id: int,
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_user_detail(user_id=user_id, db=db)


    
@app.delete("/api/v1/posts/{post_id}/")
async def delete_post(
    post_id: int,
    db: orm.Session = fastapi.Depends(services.get_db),
    user: schemas.UserRequest = fastapi.Depends(services.current_user) #solo personas autorizadas pueden borrar

):
    post = await services.get_post_detail(post_id=post_id, db=db) #schema type
    await services.delete_post(post=post, db=db) #en delete post espera un model no un schema como post

    return "Post deleted successfully"

#update post
@app.put("/api/v1/posts/{post_id}/", response_model=schemas.PostResponse)
async def update_post(
    post_id: int,
    post_request: schemas.PostRequest,
    db:orm.Session = fastapi.Depends(services.get_db)
):
    db_post = await services.get_post_detail(post_id=post_id, db=db)

    return await services.update_post(post_request=post_request,post=db_post,db=db)