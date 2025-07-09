from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel import Session, select

from app.db import get_session
from app.film.models import (
    Film,
    FilmPublic,
    FilmCreate,
    FilmUpdate,
    GenrePublic,
    GenreCreate,
    Genre,
    GenreUpdate,
)
from app.utils.exceptions import NotFoundModelException

film_router = APIRouter(prefix="/film", tags=["Film"])


@film_router.post("/genre", response_model=GenrePublic)
def create_genre(genre: GenreCreate, session: Session = Depends(get_session)):
    db_genre = Genre.model_validate(genre)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre


@film_router.get("/genre", response_model=list[GenrePublic])
def list_genres(session: Session = Depends(get_session)):
    genres = session.exec(select(Genre)).all()
    return genres


@film_router.get("/genre/{genre_id}", response_model=GenrePublic)
def get_genre(genre_id: int, session: Session = Depends(get_session)):
    if not (genre := session.get(Genre, genre_id)):
        raise NotFoundModelException(Genre)
    return genre


@film_router.post("/genre/{genre_id}", response_model=GenrePublic)
def update_genre(
    genre_id: int, genre: GenreUpdate, session: Session = Depends(get_session)
):
    if not (db_genre := session.get(Genre, genre_id)):
        raise NotFoundModelException(Genre)
    genre_data = Genre.model_dump(genre)
    db_genre.sqlmodel_update(genre_data)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre


@film_router.delete("/genre/{genre_id}")
def delete_genre(genre_id: int, session: Session = Depends(get_session)):
    if not (genre := session.get(Genre, genre_id)):
        raise NotFoundModelException(Genre)
    session.delete(genre)
    session.commit()
    return {"message": f"Successfully deleted genre with id {genre_id}"}


@film_router.get("/", response_model=list[FilmPublic])
def list_films(session: Session = Depends(get_session)):
    films = session.exec(select(Film)).all()
    return films


@film_router.post("/", response_model=FilmPublic)
def create_film(film: FilmCreate, session: Session = Depends(get_session)):
    genres = session.exec(select(Genre).where(Genre.id.in_(film.genres))).all()

    db_film = Film(name=film.name, genres=genres)
    session.add(db_film)
    session.commit()
    session.refresh(db_film)
    return db_film


@film_router.get("/{film_id}", response_model=FilmPublic)
def get_film(film_id: int, session: Session = Depends(get_session)):
    if not (film := session.get(Film, film_id)):
        raise NotFoundModelException(Film)
    return film


@film_router.post("/{film_id}", response_model=FilmPublic)
def update_film(
    film_id: int, film: FilmUpdate, session: Session = Depends(get_session)
):
    if not (db_film := session.get(Film, film_id)):
        raise NotFoundModelException(Film)

    if film.name:
        db_film.name = film.name
    if film.genres:
        genres = session.exec(select(Genre).where(Genre.id.in_(film.genres))).all()
        db_film.genres = genres

    session.add(db_film)
    session.commit()
    session.refresh(db_film)
    return db_film


@film_router.delete("/{film_id}")
def delete_film(film_id: int, session: Session = Depends(get_session)):
    if not (film := session.get(Film, film_id)):
        raise NotFoundModelException(Film)
    session.delete(film)
    session.commit()
    return {"message": f"Successfully deleted film with id {film_id}"}
