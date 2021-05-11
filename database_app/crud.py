from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database_app import models, database_schemas


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   # Creates an encryption variable


# Verifies password by checking plain with hashed passwords
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Make password hashed
def get_password_hash(password):
    return pwd_context.hash(password)


# Get user by id
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# Get user by username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


# Get all users
def get_users(db: Session):
    return db.query(models.User).all()


# Register a new user in a database
def create_user(db: Session, user: database_schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Update user info
def update_user(db: Session, user_id: int, user: database_schemas.UserUpdate):
    stored_user_data = get_user(db, user_id=user_id)

    if user.username is not None:
        stored_user_data.username = user.username

    if user.first_name is not None:
        stored_user_data.first_name = user.first_name

    if user.last_name is not None:
        stored_user_data.last_name = user.last_name

    if user.password is not None:
        hashed_password = get_password_hash(user.password)
        stored_user_data.password = hashed_password

    db.commit()
    db.refresh(stored_user_data)

    return {
        "message": "Data has been modified. If you changed password or username, authorize again"
    }


# Delete specific user by id
def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id=user_id)

    db.delete(user)
    db.commit()

    return {
        "message": "Account has been deleted. Register a new one if you want"
    }


# Delete current user
def delete_me(db: Session, user_id: int):
    user = get_user(db, user_id=user_id)

    db.delete(user)
    db.commit()

    return {
        "message": "Your account has been deleted. Register a new one or login as an existing"
    }