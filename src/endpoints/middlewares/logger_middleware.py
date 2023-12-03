import os
import logging
from typing import Callable

from starlette.middleware.base import StreamingResponse
from fastapi import Request
from dependency_injector.wiring import inject, Provide

from src.core.containers import Container


class LoggerMiddleware:
    @inject
    def __init__(self, config: dict = Provide[Container.config]):
        self.config = config
        self.http_log = logging.getLogger(config['HTTP_LOG_NAME'])
        self.business_logic_log = logging.getLogger(config['BUSINESS_LOGIC_LOG_NAME'])
        self.set_loggers()

    async def __call__(self,
                       request: Request,
                       call_next: Callable):
        try:
            response: StreamingResponse = await call_next(request)
            self.http_log.info(self.http_message_log(request, response))
        except Exception as e:
            self.business_logic_log.error(self.business_logic_message_log(request, e))
            raise e

        return response

    def set_loggers(self) -> None:
        formatter = logging.Formatter(
            '"TIME": %(asctime)s - "LEVEL": %(levelname)s - %(message)s'
        )

        dir_path = os.path.join(self.config['BASE_DIR'], self.config['LOG_DIR'])
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        self.http_log.handlers.clear()
        self.business_logic_log.handlers.clear()

        self.http_log.setLevel(logging.INFO)
        self.business_logic_log.setLevel(logging.ERROR)

        http_path = os.path.join(dir_path, self.config['HTTP_LOG_NAME'])
        http_handler = logging.FileHandler(http_path)
        http_handler.setFormatter(formatter)

        business_logic_path = os.path.join(dir_path, self.config['BUSINESS_LOGIC_LOG_NAME'])
        business_logic_handler = logging.FileHandler(business_logic_path)
        business_logic_handler.setFormatter(formatter)

        self.http_log.addHandler(http_handler)
        self.business_logic_log.addHandler(business_logic_handler)

    @staticmethod
    def http_message_log(request: Request, response: StreamingResponse) -> str:
        data = {
            'IP': request.client.host,
            'API': request.url.path,
            'METHOD': request.method,
            'PATH PARAMS': request.path_params,
            'QUERY PARAMS': request.query_params,
            'STATUS CODE': response.status_code
        }
        return ' - '.join([f'"{key}": {value}' for key, value in data.items()])

    @staticmethod
    def business_logic_message_log(request: Request, e: Exception):
        data = {
            'IP': request.client.host,
            'API': request.url.path,
            'METHOD': request.method,
            'PATH PARAMS': request.path_params,
            'QUERY PARAMS': request.query_params,
            'exc': e
        }
        return ' - '.join([f'"{key}": {value}' for key, value in data.items()])