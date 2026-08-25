from pydantic import BaseModel, EmailStr, Field


class UsersBase(BaseModel):
    name: str = Field(min_length=2, max_length=500)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserResponse(BaseModel):
    name: str
    email: str
    role: str

    class config:
        from_attributes = True
