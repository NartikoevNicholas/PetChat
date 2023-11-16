import abc

from fastapi import status

from .abstract_exception import AbstractHTTPException


class BadRequestHTTPException(AbstractHTTPException, abc.ABC):
    status_code = status.HTTP_400_BAD_REQUEST


class BadRequestLogoutHTTPException(BadRequestHTTPException):
    detail_message = 'Bad request'


class BadRequestJWTExpiredHTTPException(BadRequestHTTPException):
    detail_message = 'Token is expired'


class BadRequestJWTHTTPException(BadRequestHTTPException):
    detail_message = 'Bad jwt token!'
