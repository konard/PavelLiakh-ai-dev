from typing import Optional
from tinydb import Query
from src.app.domain.story import Story
from src.infrastructure.db.json_storage import JsonStorage


class StoryStorage:
    def __init__(self, storage: JsonStorage, log):
        self.storage = storage
        self.log = log
        self.story_db = self.storage.get_db("stories")

    def get_story(self, story_number: int) -> Optional[Story]:
        return self.storage._find_entity(
            db=self.story_db, query=Query().number == story_number, entity_class=Story
        )

    def save_story(self, story: Story) -> Story:
        return self.storage.save_entity(
            db=self.story_db, query=Query().number == story.number, entity=story, entity_class=Story
        )

    def get_all(self) -> list[Story]:
        return [Story(**user_data) for user_data in self.story_db.all()]

    def get_stories_by_state(self, state) -> list[Story]:
        all = self.get_all()
        return [story for story in all if story.state and state == story.state]
