from src.app.service.development_service import DevelopmentService
from src.app.service.story_service import StoryService
from src.app.service.pr_tracking_service import PullRequestTrackingService
from src.infrastructure.github.issues_client import IssuesClient


class AiDevWorkflow:
    def __init__(
        self,
        issues_client: IssuesClient,
        story_service: StoryService,
        development_service: DevelopmentService,
        pr_tracking_service: PullRequestTrackingService,
        log,
    ):
        self.issues_client = issues_client
        self.development_service = development_service
        self.story_service = story_service
        self.pr_tracking_service = pr_tracking_service
        self.log = log

    def run_ai_dev_workflow(self) -> None:
        self._find_updates()
        self._process()
        self._track_pull_requests()

    def _find_updates(self) -> None:
        issues = self.issues_client.get_opened_issues()
        self.log.info(f"Checking {len(issues)} open issues for updates")
        for issue in issues:
            self.story_service.check_for_update(issue)

    def _process(self):
        new_stories = self.story_service.get_new_stories()
        if new_stories:
            self.log.info(f"Found {len(new_stories)} new stories to plan")

        for story in new_stories:
            self.log.info(f"Implementing story {story.name}")
            self.development_service.implement(story)

    def _track_pull_requests(self):
        """Track and manage open pull requests."""
        self.log.info("Tracking pull requests")
        self.pr_tracking_service.track_pull_requests()
