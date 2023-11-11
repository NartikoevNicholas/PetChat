import json
from fastapi import status
from fastapi.exceptions import HTTPException


class DuplicateHTTPException(HTTPException):
    def __init__(
        self,
        content: str,
        headers=None,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    ) -> None:
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
