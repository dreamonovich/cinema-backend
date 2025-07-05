from sqlmodel import SQLModel
from starlette.exceptions import HTTPException


class NotFoundModelException(HTTPException):
    def __init__(self, model_class: SQLModel) -> None:
        detail = f"{model_class.__name__} is not found"
        super().__init__(status_code=404, detail=detail)
