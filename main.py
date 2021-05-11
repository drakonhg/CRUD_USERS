from typing import List
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

import config
from database_app import crud, models, database_schemas
from database_app.database import SessionLocal, engine
from authentication_app import token, token_schemas

models.Base.metadata.create_all(bind=engine)  # Running model engine to connect database

app = FastAPI()  # Creating an Fast Api

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Creating oauth scheme to authorize


# Creates dependency for database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Authenticate user and return user data if exist else return False
def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db=db, username=username)
    if not user:
        return False
    if not crud.verify_password(password, user.hashed_password):
        return False
    return user


# Getting current user that is accessing API
async def get_current_user(db: Session = Depends(get_db), bearer_token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(bearer_token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = token_schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


"""
Endpoints
"""


# Register user and creates data in database
@app.post("/register/", response_model=database_schemas.User, status_code=201)
async def register(user: database_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)


# Login user to see access token, which is inside Headers
@app.post("/login/", response_model=token_schemas.Token)
async def login_for_access_token(db: Session = Depends(get_db),
                                 form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(config.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = token.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Showing list of all users
@app.get("/users/", response_model=List[database_schemas.User])
async def get_users(db: Session = Depends(get_db),
                    bearer_token: str = Depends(oauth2_scheme)):
    if bearer_token:
        users = crud.get_users(db)
        return users


# Getting user data by id
@app.get("/users/{user_id}/", response_model=database_schemas.User)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db),
                         bearer_token: str = Depends(oauth2_scheme)):
    if bearer_token:
        db_user = crud.get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user


# Getting current user data
@app.get("/user/me/", response_model=database_schemas.User, status_code=200)
async def get_my_user_data(current_user: database_schemas.User = Depends(get_current_user)):
    return current_user


# Updating current user data
@app.patch("/user/me/edit/", status_code=201)
async def update_my_data(user_data: database_schemas.UserUpdate,
                         db: Session = Depends(get_db),
                         current_user: database_schemas.User = Depends(get_current_user)):
    print(current_user.id)
    return crud.update_user(db, current_user.id, user_data)


# Deleting user data by id
@app.delete('/users/{user_id}/delete/')
async def delete_user_account(user_id: int, db: Session = Depends(get_db),
                              bearer_token: str = Depends(oauth2_scheme)):
    if not bearer_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User is not found")
    return crud.delete_user(db, user_id)


# Deleting current user data
@app.delete('/user/me/delete/', status_code=200)
async def delete_my_account(db: Session = Depends(get_db),
                            current_user: database_schemas.User = Depends(get_current_user)):
    if not current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User is not found")
    return crud.delete_me(db, user_id=current_user.id)
