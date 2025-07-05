from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel import Session, select

from app.cinema.models import CinemaCreate, CinemaPublic, Cinema, CinemaUpdate
from app.cinema.routers.hall_router import hall_router
from app.db import get_session
from app.utils.exceptions import NotFoundModelException

cinema_router = APIRouter(prefix="/cinema", tags=["Cinema"])


@cinema_router.post("/", response_model=CinemaPublic)
def create_cinema(cinema: CinemaCreate, session: Session = Depends(get_session)):
    db_cinema = Cinema.model_validate(cinema)
    session.add(db_cinema)
    session.commit()
    session.refresh(db_cinema)
    return db_cinema


@cinema_router.get("/", response_model=list[CinemaPublic])
def list_cinema(session: Session = Depends(get_session)):
    cinemas = session.exec(select(Cinema)).all()
    return cinemas


@cinema_router.get("/{cinema_id}", response_model=CinemaPublic)
def get_cinema(cinema_id: int, session: Session = Depends(get_session)):
    if not (cinema := session.get(Cinema, cinema_id)):
        raise NotFoundModelException(Cinema)
    return cinema


@cinema_router.patch("/{cinema_id}", response_model=CinemaPublic)
def update_cinema(
    cinema_id: int, cinema: CinemaUpdate, session: Session = Depends(get_session)
):
    if not (db_cinema := session.get(Cinema, cinema_id)):
        raise NotFoundModelException(Cinema)
    cinema_data = cinema.model_dump(exclude_unset=True)
    db_cinema.sqlmodel_update(cinema_data)
    session.add(db_cinema)
    session.commit()
    session.refresh(db_cinema)
    return db_cinema


@cinema_router.delete("/{cinema_id}")
def delete_cinema(cinema_id: int, session: Session = Depends(get_session)):
    if not (cinema := session.get(Cinema, cinema_id)):
        raise NotFoundModelException(Cinema)
    session.delete(cinema)
    session.commit()
    return {"message": f"Successfully deleted cinema with id {cinema_id}"}


cinema_router.include_router(hall_router, prefix="/{cinema_id}")
