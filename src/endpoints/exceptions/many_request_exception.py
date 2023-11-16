from fastapi import status

from .abstract_exception import AbstractHTTPException


class ManyRequestsHTTPException(AbstractHTTPException):
    status_code: int = status.HTTP_429_TOO_MANY_REQUESTS
    detail_message = 'Too many request'
