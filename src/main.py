import uvicorn

from src import get_application
from src.core.config import get_config


settings = get_config()
app = get_application(
    settings=settings
)


if __name__ == '__main__':
    uvicorn.run(
        'src.main:app',
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=True
    )
