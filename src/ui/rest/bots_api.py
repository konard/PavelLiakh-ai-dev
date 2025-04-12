import time

from fastapi import Request
from fastapi.responses import JSONResponse

from src.app.register.data_analyst import analyze_task
from src.infrastructure.telegram.telegram_bots import (
    dispatch_manager_update,
    dispatch_example_update,
    dispatch_rnp_update,
)
from src.infrastructure.web_server import web_app as web_app
from src.ioc import log


@web_app.post("/webhook/manager")
async def manager_webhook(request: Request):
    """Handle manager bot webhook requests."""
    log.info("Received manager webhook request.")
    update = await request.json()
    log.info(f"Received manager update: {update}")
    await dispatch_manager_update(update)


@web_app.post("/webhook/example")
async def example_webhook(request: Request):
    """Handle example bot webhook requests."""
    log.info("Received example webhook request.")
    update = await request.json()
    log.info(f"Received example update: {update}")
    await dispatch_example_update(update)


@web_app.post("/webhook/rnp")
async def rnp_webhook(request: Request):
    """Handle RNP bot webhook requests."""
    log.info("Received RNP webhook request.")
    update = await request.json()
    log.info(f"Received RNP update: {update}")
    await dispatch_rnp_update(update)


@web_app.post("/adam")
async def ask_adam(request: Request):
    """Ask Adam a question."""
    question_json = await request.json()
    question = question_json.get("question")
    if question is None:
        return JSONResponse(content={"error": "No question provided"}, status_code=400)

    log.info(f"Received question to ADAM: {question}")
    # I want to calculate a time
    start_time = time.time()

    response = analyze_task(question).concrete_answer
    end_time = time.time()
    time_taken = end_time - start_time
    log.info(f"Response from ADAM ({time_taken}): {response}")
    return response
