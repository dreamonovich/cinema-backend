from typing import Optional

from sqlmodel import SQLModel, Field


class CinemaBase(SQLModel):
    name: str
    address: str
    latitude: float
    longitude: float


class Cinema(CinemaBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, default=None)


class CinemaPublic(Cinema):
    pass


class CinemaCreate(CinemaBase):
    pass


class CinemaUpdate(SQLModel):
    name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class CinemaHallBase(SQLModel):
    name: str
    capacity: int
    is_vip: bool


class CinemaHall(CinemaHallBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, default=None)

    cinema_id: int = Field(foreign_key="cinema.id")


class CinemaHallPublic(CinemaHall):
    pass


class CinemaHallCreate(CinemaHallBase):
    pass


class CinemaHallUpdate(SQLModel):
    name: str | None = None
    capacity: int | None = None
    is_vip: bool | None = None
