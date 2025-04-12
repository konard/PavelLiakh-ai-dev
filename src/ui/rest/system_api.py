import os
import signal

from fastapi import Request, Form
from fastapi.responses import JSONResponse

from src.config import config
from src.infrastructure.web_server import web_app as web_app
from src.ioc import log, client_service


@web_app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})


@web_app.get("/stop")
async def stop_server():
    """Stop the server gracefully."""
    log.info("Received stop request, shutting down...")
    os.kill(os.getpid(), signal.SIGINT)
    return JSONResponse(content={"status": "shutting down"})


@web_app.get("/version")
async def get_version():
    return JSONResponse(content={"version": config.version})


from pydantic import BaseModel

class RegisterRequest(BaseModel):
    name: str
    email: str
    article_number: str

@web_app.post("/register")
async def register_user(request: RegisterRequest):
    """Handle registration form submissions from the website"""
    try:
        # Register new client using IoC-injected service
        client = client_service.register_client(
            name=request.name,
            email=request.email,
            sku_number=request.article_number
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Registration successful",
                "client_email": client.email
            }
        )
    except Exception as e:
        log.error(f"Registration failed: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Registration failed",
                "error": str(e)
            }
        )
