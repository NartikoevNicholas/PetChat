from fastapi import status

from .abstract_exception import AbstractHTTPException


class UnauthorizedHTTPException(AbstractHTTPException):
    status_code: int = status.HTTP_401_UNAUTHORIZED,
    detail_message = 'Incorrect username or password'
