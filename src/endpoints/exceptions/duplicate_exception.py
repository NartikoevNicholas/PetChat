import abc

from fastapi import status

from .abstract_exception import AbstractHTTPException


class DuplicateHTTPException(AbstractHTTPException, abc.ABC):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class DuplicateUserEmailHTTPException(DuplicateHTTPException):
    detail_message = 'Email is exists'


class DuplicateUserUsernameHTTPException(DuplicateHTTPException):
    detail_message = 'Username is exists'
