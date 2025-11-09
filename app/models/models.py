from typing import Optional
from datetime import date, datetime, timezone
from sqlmodel import SQLModel, Field, Relationship


def utc_now():
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    fullname: Optional[str] = None
    email: Optional[str] = Field(default=None, index=True)
    hashed_password: str
    role: str = "user"  # Пользователи имеют роли admin, user
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)


class Privilege(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class Citizen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lastname: str
    firstname: str
    middlename: Optional[str] = None
    id_snils: Optional[str] = Field(default=None, unique=True)
    privilege_id: Optional[int] = Field(default=None, foreign_key="privilege.id")
    created_at: datetime = Field(default_factory=utc_now)


class Certificates(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    citizen_id: Optional[int] = Field(default=None, foreign_key="citizen.id")
    number_certificate: Optional[str] = None
    issue_date: Optional[date] = None
    issued_by: Optional[str] = None
    purpose: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class EventLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
