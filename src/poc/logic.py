from src.app.domain.story import Story
from src.ioc import planner_service


def build_plan(task: str) -> str:
    story = Story(description=task)

    plan = planner_service.plan(story)

    # For now just return a simple response, but this could call LLM later
    return f"Task: {task}\n\nPlan:\n{plan}"
