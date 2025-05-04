import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent

app = FastAPI()
mcp_app = MCPApp(name="file_tree_server")

class CommandRequest(BaseModel):
    command: str

@app.on_event("startup")
async def startup_event():
    await mcp_app.__aenter__()

@app.on_event("shutdown")
async def shutdown_event():
    await mcp_app.__aexit__(None, None, None)

@app.post("/handle")
async def handle_command(request: CommandRequest):
    command = request.command.lower()
    logger = mcp_app.logger

    agent = Agent(
        name="file_tree_agent",
        instruction="Редактирует файлы или строит дерево директорий.",
        server_names=["filesystem"],
    )

    async with agent:
        tools_response = await agent.list_tools()
        logger.debug(f"Полный ответ tools.list(): {tools_response}")

        if isinstance(tools_response, dict) and "data" in tools_response:
            tools_list = tools_response["data"].get("tools", [])
            logger.info(f"Доступные инструменты: {[tool['name'] for tool in tools_list]}")
        else:
            logger.error("Неправильный формат ответа от list_tools()")
            raise HTTPException(status_code=500, detail="Ошибка при получении инструментов")

        if command == "file":
            try:
                response = await agent.call_tool(
                    tool_name="edit_file",
                    params={
                        "path": "test.txt",
                        "edits": [{"oldText": "old", "newText": "new"}],
                        "dryRun": False,
                    },
                )
                return {"status": "success", "diff": response.get("diff")}
            except Exception as e:
                logger.error(f"Ошибка при редактировании: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        elif command == "tree":
            try:
                response = await agent.call_tool(
                    tool_name="directory_tree",
                    params={"path": "."},
                )
                return {"status": "success", "tree": response}
            except Exception as e:
                logger.error(f"Ошибка при построении дерева: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        else:
            logger.error("Неверная команда")
            raise HTTPException(status_code=400, detail="Неверная команда: используйте 'file' или 'tree'")
