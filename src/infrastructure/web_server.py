import uvicorn
from fastapi import FastAPI

web_app = FastAPI()


def run_webserver():
    print("Starting FastAPI server in production mode")
    uvicorn.run(
        web_app,
        host="0.0.0.0",
        port=80,
    )
