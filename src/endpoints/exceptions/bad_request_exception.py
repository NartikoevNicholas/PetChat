import abc

from fastapi import status

from .abstract_exception import AbstractHTTPException


class AbstractBadRequestHTTPException(AbstractHTTPException, abc.ABC):
    status_code = status.HTTP_400_BAD_REQUEST


class BadRequestHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Bad request'


class TokenExpiredHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'JWT token is expired!'


class TokenInvalidHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Bad jwt token!'


class TokenTypeInvalidHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Invalid token type '


class TokenDeletedHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Token is deleted!'


class TokenLogoutHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Invalid logout'


class UserNotFoundHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'User not Found!'


class NeedEmailVerifyHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Need verify email!'


class EmailBusyHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Email is busy!'


class UsernameBusyHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Username is busy!'


class InvalidPasswordHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Invalid password!'


class InvalidLinkHTTPException(AbstractBadRequestHTTPException):
    detail_message = 'Invalid link!'
