from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import models
from app.dependencies.auth import create_access_token, role_checker
from app.dependencies.common import current_user_dependency, db_dependency
from app.schemas import (
    UserResponse,
    UsersBase,
)
from utils import hashPassword, verifyPassword

router = APIRouter(tags=["Users"])


@router.post("/user/signup", status_code=status.HTTP_201_CREATED)
def userSignUp(userDetails: UsersBase, db: db_dependency):
    hashed_password = hashPassword(userDetails.password)

    db_user = models.User(
        name=userDetails.name,
        email=userDetails.email,
        password=hashed_password,
        role="customer",
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/users", status_code=status.HTTP_200_OK)
def getUsersList(db: db_dependency):
    users = db.query(models.User).all()
    return users


# used for swagger
@router.post("/user/login/oauth2", status_code=status.HTTP_200_OK)
def userLogin(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = (
        db.query(models.User).filter(models.User.email == form_data.username).first()
    )
    print(form_data, "form_data")

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with {form_data.username} not found ",
        )

    if not verifyPassword(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    access_token = create_access_token(db_user.id)

    return {"access_token": access_token, "token_type": "bearer"}


# used for postman/React app
"""
@router.post("/user/login", status_code=status.HTTP_200_OK)
def userLogin(db: db_dependency, form_data: UserResponse):
    db_user = db.query(models.User).filter(models.User.email == form_data.email).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with {form_data.email} not found ",
        )

    if not verifyPassword(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    access_token = create_access_token(db_user.id)

    return {"access_token": access_token, "token_type": "bearer"}
"""


@router.get("/users/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_my_profile(current_user: current_user_dependency):
    return current_user


@router.put(
    "/update/role",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_checker("admin"))],
)
def updateUserRole(
    user_id: int,
    user_role: str,
    db: db_dependency,
):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    print(user_role, user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user not found with {user_id}.",
        )

    try:
        role = models.UserRoles(user_role)
    except ValueError as e:
        return f"an error occured {e}."

    user.role = role

    db.commit()
    db.refresh(user)

    return user
