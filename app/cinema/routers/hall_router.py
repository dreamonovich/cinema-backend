from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Form
from sqlalchemy import delete
from sqlmodel import Session, select

from app.cinema.models import (
    CinemaHallPublic,
    CinemaHallCreate,
    Cinema,
    CinemaHall,
    CinemaHallUpdate, Seat, SeatHallLink,
)
from app.db import get_session
from app.minio import minio_handler
from app.utils.exceptions import NotFoundModelException
from app.utils.svg import process_scheme

hall_router = APIRouter(prefix="/hall", tags=["Hall"])


@hall_router.post("/", response_model=CinemaHallPublic)
def create_hall(
    cinema_id: int, hall: CinemaHallCreate, session: Session = Depends(get_session)
):
    if not (cinema := session.get(Cinema, cinema_id)):
        raise NotFoundModelException(Cinema)
    db_hall = CinemaHall(**hall.model_dump(), cinema_id=cinema_id)
    session.add(db_hall)
    session.commit()
    session.refresh(db_hall)
    return db_hall


@hall_router.get("/{hall_id}", response_model=CinemaHallPublic)
def get_hall(cinema_id: int, hall_id: int, session: Session = Depends(get_session)):
    if not (
        hall := session.exec(
            select(CinemaHall).where(
                CinemaHall.cinema_id == cinema_id, CinemaHall.id == hall_id
            )
        ).first()
    ):
        raise NotFoundModelException(CinemaHall)

    return hall


@hall_router.patch("/{hall_id}", response_model=CinemaHallPublic)
def update_hall(
    cinema_id: int,
    hall_id: int,
    hall: CinemaHallUpdate,
    session: Session = Depends(get_session),
):
    if not (
        db_hall := session.exec(
            select(CinemaHall).where(
                CinemaHall.cinema_id == cinema_id, CinemaHall.id == hall_id
            )
        ).first()
    ):
        raise NotFoundModelException(CinemaHall)
    hall_data = CinemaHall.model_dump(hall)
    db_hall.sqlmodel_update(hall_data)
    session.add(db_hall)
    session.commit()
    session.refresh(db_hall)
    return db_hall


@hall_router.delete("/{hall_id}")
def delete_hall(cinema_id: int, hall_id: int, session: Session = Depends(get_session)):
    if not (
        hall := session.exec(
            select(CinemaHall).where(
                CinemaHall.cinema_id == cinema_id, CinemaHall.id == hall_id
            )
        ).first()
    ):
        raise NotFoundModelException(CinemaHall)
    session.delete(hall)
    session.commit()
    return {"message": f"Successfully deleted hall with id {hall_id}"}


@hall_router.get("/", response_model=list[CinemaHallPublic])
def list_hall(cinema_id: int, session: Session = Depends(get_session)):
    if not (cinema := session.get(Cinema, cinema_id)):
        raise NotFoundModelException(Cinema)
    statement = select(CinemaHall).where(CinemaHall.cinema_id == cinema.id)
    halls = session.exec(statement).all()

    return halls

@hall_router.post("/{hall_id}/scheme")
def upload_scheme(svg_file: UploadFile, cinema_id: int, hall_id: int, session: Session = Depends(get_session)):
    if not (
        hall := session.exec(
            select(CinemaHall).where(
                CinemaHall.cinema_id == cinema_id, CinemaHall.id == hall_id
            )
        ).first()
    ):
        raise NotFoundModelException(CinemaHall)

    seat_ids = [seat.id for seat in hall.seats]
    session.exec(delete(SeatHallLink).where(SeatHallLink.seat_id.in_(seat_ids)))
    session.exec(delete(Seat).where(Seat.id.in_(seat_ids)))
    session.commit()

    scheme, seats = process_scheme(svg_file.file)

    scheme_object_name = f"cinema_{cinema_id}/hall_{hall_id}.svg"
    minio_handler.upload_file(scheme_object_name, scheme, scheme.getbuffer().nbytes)

    print(seats)
    hall.scheme = scheme_object_name
    for seat in seats:
        seat.hall = hall

    session.add_all([hall] + seats)
    session.commit()

    url = minio_handler.get_url(scheme_object_name)

    return {"object_name": scheme_object_name, "download_url": url}
