from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel import Session

from app.cinema.models import CinemaHall
from app.db import get_session
from app.film.models import FilmScreeningPublic, FilmScreeningCreate, FilmScreening, Film, FilmScreeningUpdate
from app.utils.exceptions import NotFoundModelException

screening_router = APIRouter(prefix="/screening", tags=["Screening"])

@screening_router.post("/", response_model=FilmScreeningPublic)
def create_screening(screening: FilmScreeningCreate, session: Session = Depends(get_session)):

    if not (film := session.get(Film, screening.film_id)):
        raise NotFoundModelException(Film)
    if not (hall := session.get(CinemaHall, screening.hall_id)):
        raise NotFoundModelException(CinemaHall)

    db_screening = FilmScreening.model_validate(screening)

    db_screening.film = film
    db_screening.hall = hall

    session.add(db_screening)
    session.commit()
    session.refresh(db_screening)

    return db_screening

@screening_router.get("/{screening_id}", response_model=FilmScreeningPublic)
def get_screening(screening_id: int, session: Session = Depends(get_session)):
    if not (screening := session.get(FilmScreening, screening_id)):
        raise NotFoundModelException(FilmScreening)

    return screening

@screening_router.post("/{screening_id}", response_model=FilmScreeningPublic)
def update_screening(
    screening_id: int, screening: FilmScreeningUpdate, session: Session = Depends(get_session)
):
    if not (db_screening := session.get(FilmScreening, screening_id)):
        raise NotFoundModelException(FilmScreening)
    if screening.film_id and not (db_film := session.get(Film, screening.film_id)):
        raise NotFoundModelException(Film)
    if screening.hall_id and not (db_hall := session.get(CinemaHall, screening.hall_id)):
        raise NotFoundModelException(Film)

    if screening.date:
        db_screening.date = screening.date
    if screening.film_id:
        db_screening.film = db_film
        db_screening.film_id = screening.film_id
    if screening.hall_id:
        db_screening.hall = db_hall
        db_screening.hall_id = screening.hall_id


    session.add(db_screening)
    session.commit()
    session.refresh(db_screening)
    return db_screening


@screening_router.delete("/{screening_id}")
def delete_screening(screening_id: int, session: Session = Depends(get_session)):
    if not (creening := session.get(FilmScreening, screening_id)):
        raise NotFoundModelException(FilmScreening)
    session.delete(creening)
    session.commit()
    return {"message": f"Successfully deleted film with id {screening_id}"}
