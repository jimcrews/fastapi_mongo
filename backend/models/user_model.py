from enum import Enum

from pydantic import EmailStr, Field, BaseModel, validator

from email_validator import validate_email, EmailNotValidError


class Role(str, Enum):
    SALESMAN = "SALESMAN"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=15)
    email: str = Field(...)
    password: str = Field(...)
    role: Role

    @validator("email")
    def valid_email(cls, v):
        try:
            email = validate_email(v).email
            return email
        except EmailNotValidError:
            raise EmailNotValidError


class LoginBase(BaseModel):
    email: str = EmailStr()
    password: str = Field(...)


class CurrentUser(BaseModel):
    email: str = EmailStr()
    username: str = Field(...)
    role: str = Field(...)
