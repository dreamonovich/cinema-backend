from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class FilmGenreLink(SQLModel, table=True):
    film_id: int = Field(foreign_key="film.id", primary_key=True)
    genre_id: int = Field(foreign_key="genre.id", primary_key=True)


class Genre(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    films: List["Film"] = Relationship(
        back_populates="genres", link_model=FilmGenreLink
    )


class GenrePublic(SQLModel):
    id: int
    name: str


class GenreCreate(SQLModel):
    name: str


class GenreUpdate(SQLModel):
    name: str


class FilmBase(SQLModel):
    name: str


class Film(FilmBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    genres: List[Genre] = Relationship(back_populates="films", link_model=FilmGenreLink)


class FilmCreate(SQLModel):
    name: str
    genres: list[int]


class FilmPublic(SQLModel):
    id: int
    name: str
    genres: List[GenrePublic]


class FilmUpdate(SQLModel):
    name: str | None = None
    genres: list[int] | None = None
