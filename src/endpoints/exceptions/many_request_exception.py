from fastapi import status
from fastapi.exceptions import HTTPException


class ManyRequestsHTTPException(HTTPException):
    def __init__(
        self,
        content: str = 'Too many request',
        headers: dict = None,
        status_code: int = status.HTTP_429_TOO_MANY_REQUESTS
    ):
        content = {
            'detail': [
                {
                    'loc': ['string', 0],
                    'msg': content,
                    'type': 'string'
                }
            ]
        }
        super().__init__(status_code, content, headers)
