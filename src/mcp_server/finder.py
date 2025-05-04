import asyncio
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent

app = MCPApp(name="file_tree_app")

async def handle_command(command: str):
    logger = app.logger

    agent = Agent(
        name="file_tree_agent",
        instruction="Редактирует файлы или строит дерево директорий.",
        server_names=["filesystem"],
    )

    async with agent:
        tools_response = await agent.list_tools()
        logger.debug(f"Полный ответ tools.list(): {tools_response}")

        tool_names = [tool.name for tool in tools_response.tools]
        print("Доступные тулзы:", tool_names)


        if command == "file":
            try:
                response = await agent.call_tool(
                    tool_name="filesystem_edit_file",
                    params={
                        "path": "test.txt",
                        "edits": [{"oldText": "old", "newText": "new"}],
                        "dryRun": False,
                    },
                )
                print(f"Файл изменён. Diff: {response.get('diff')}")
            except Exception as e:
                print(f"Ошибка при редактировании: {e}")

        elif command == "tree":
            try:
                response = await agent.call_tool(
                    tool_name="filesystem_directory_tree",
                    params={"path": "."},
                )
                print(f"Дерево директорий: {response}")
            except Exception as e:
                print(f"Ошибка при построении дерева: {e}")
        else:
            print("Неизвестная команда. Введите 'file' или 'tree'.")

async def main():
    app.run()  # Запуск MCPApp
    try:
        print("Добро пожаловать! Введите команду ('file', 'tree' или 'exit'):")

        while True:
            command = input(">>> ").strip().lower()
            if command == "exit":
                print("Завершение работы.")
                break
            await handle_command(command)
    finally:
        await app.cleanup()  # Завершение MCPApp

if __name__ == "__main__":
    asyncio.run(main())
