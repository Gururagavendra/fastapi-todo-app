from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

def classify_db_error(exc: SQLAlchemyError) -> tuple[int, str]:
    if isinstance(exc, IntegrityError):
        msg = str(exc.orig) if exc.orig else "Integrity constraint violated"
        column = msg.split(":")[-1].strip().split(".")[-1] if ":" in msg else "field"
        return status.HTTP_400_BAD_REQUEST, f"{column} already in use."
    return status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error."