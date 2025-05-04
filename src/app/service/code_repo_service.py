mocked_repo_tree = """
D:.
|   config.py
|   ioc.py
|   main.py
+---app
|   |   ai_dev_workflow.py
|   +---domain
|   |   |   story.py
|   +---service
|   |   |   code_repo_service.py
|   |   |   code_request_service.py
|   |   |   development_service.py
|   |   |   planner_service.py
|   |   |   story_service.py
+---example_code
|       github_client.py
|       git_handler.py
|       gpt_client.py
|       main.py
+---infrastructure
|   |   logger.py
|   |   web_server.py
|   +---ai
|   |   |   llm_client.py
|   |   |   llm_client_mock.py
|   |   |   prompt.py
|   +---ci
|   |   |   code_builder.py
|   +---db
|   |   |   json_storage.py
|   |   |   story_storage.py
|   +---github
|   |   |   issues_client.py
|   |   |   repository_client.py
+---poc
|   |   logic.py
|   |   runner.py
|   |   ui.py
|   |
|   +---logs
+---ui
|   \---site
|       |   gui.py
"""

mocked_file_spec = """
{
    "content": "first code line\nsecond code line",
    "specification": {
        "function1": {
            "params": "param1, param2",
            "returns": "str"
        }
    }
}
"""


class CodeRepoServise:
    def __init__(self, log):
        self.log = log

    def get_files_tree(self) -> str:
        return mocked_repo_tree

    def get_file_info(self, repo_file_path: str) -> str:
        return mocked_file_spec
