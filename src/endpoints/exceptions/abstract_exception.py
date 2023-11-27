import abc
import typing as tp

from fastapi.exceptions import HTTPException


class AbstractHTTPException(HTTPException, abc.ABC):
    status_code: int
    detail_message: str
    headers: tp.Optional[tp.Dict[str, str]] = None

    def __init__(
        self,
        status_code: tp.Optional[int] = None,
        detail_message: tp.Optional[str] = None,
        headers: tp.Optional[tp.Dict[str, str]] = None
    ):
        if status_code is not None:
            self.status_code = status_code
        if detail_message is not None:
            self.detail_message = detail_message
        if headers is not None:
            self.headers = headers

        super().__init__(self.status_code, self.get_detail(), self.headers)

    def get_detail(self) -> tp.Union[str, dict]:
        content = {
            'loc': ['string', 0],
            'msg': self.detail_message,
            'type': 'string'
        }
        return content

    # def get_detail_for_test(self):
    #     content = {
    #         'detail': []
    #     return content