from src.infrastructure.github.issues_client import IssuesClient


class StoryWorkflow:
    def __init__(self, issues_client: IssuesClient):
        self.issues_client = issues_client

    def find_updates(self):
        self.issues_client.get_issues()
        # 1 read stories in github
        # 2 filter those are with label `TODO`
        # 3 store new to DB
        # 4 replace github label with  `IN_PROGRESS`

        print(f"Finding updates for the story: {self.story.title}")
        # Additional logic to find updates in the story workflow

    def start(self):


        print(f"Starting the story: {self.story.title}")
        # Additional logic to start the story workflow

    def progress(self):
        print(f"Progressing the story: {self.story.title}")
        # Additional logic to progress the story workflow

    def complete(self):
        print(f"Completing the story: {self.story.title}")
        # Additional logic to complete the story workflow