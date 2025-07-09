import uuid
from typing import Optional, List

from pydantic import AnyUrl, computed_field
from sqlmodel import SQLModel, Field, Relationship

from app.minio import minio_handler


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

class SeatHallLink(SQLModel, table=True):
    seat_id: uuid.UUID = Field(foreign_key="seat.id", primary_key=True)
    hall_id: int = Field(foreign_key="cinemahall.id", primary_key=True)

class CinemaHallBase(SQLModel):
    name: str
    capacity: int
    is_vip: bool


class CinemaHall(CinemaHallBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, default=None)

    scheme: str

    cinema_id: int = Field(foreign_key="cinema.id")
    screenings: List["FilmScreening"] = Relationship(back_populates="hall")
    seats: List["Seat"] = Relationship(back_populates="hall", link_model=SeatHallLink)


class CinemaHallPublic(SQLModel):
    id: int
    name: str
    capacity: int
    is_vip: bool
    cinema_id: int = Field(foreign_key="cinema.id")
    seats: List["SeatPublic"]
    scheme: str = Field(exclude=True)

    @computed_field(return_type=str)
    def scheme_url(self) -> str:
        return minio_handler.get_url(self.scheme)


class CinemaHallCreate(CinemaHallBase):
    pass


class CinemaHallUpdate(SQLModel):
    name: str | None = None
    capacity: int | None = None
    is_vip: bool | None = None

class Seat(SQLModel, table=True):
    id: uuid.UUID = Field(default=None, primary_key=True)

    row: int
    column: int

    hall: CinemaHall = Relationship(back_populates="seats", link_model=SeatHallLink)

class SeatPublic(SQLModel):
    id: uuid.UUID
    row: int
    column: int