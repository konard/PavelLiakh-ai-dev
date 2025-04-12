import uvicorn
from fastapi import FastAPI

from src.config import config
web_app = FastAPI()


def run_webserver():
    """Start FastAPI server."""
    if config.is_prod():
        print("Starting FastAPI server in production mode")
        uvicorn.run(
            web_app,
            host="0.0.0.0",
            port=config.port,
            ssl_keyfile=config.cert_key,
            ssl_certfile=config.cert,
        )
    else:
        print("Starting FastAPI server in development mode")
        uvicorn.run(web_app, host="0.0.0.0", port=config.port)
