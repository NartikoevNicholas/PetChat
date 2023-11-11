import uvicorn

from src import get_application
from src.core.config import get_config


app = get_application()
config = get_config()


if __name__ == '__main__':
    uvicorn.run(
        'src.main:app',
        host=config.UVICORN_HOST,
        port=config.UVICORN_PORT,
        reload=True
    )
