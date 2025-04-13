from typing import Optional
from tinydb import Query
from src.app.domain.story import Story
from src.infrastructure.db.json_storage import JsonStorage


class StoryStorage:
    def __init__(self, storage: JsonStorage, log):
        self.storage = storage
        self.log = log
        self.story_db = self.storage.get_db("story")

    def get_story(self, story_number: int) -> Optional[Story]:
        """Get story by GitHub issue number"""
        return self.storage._find_entity(
            db=self.story_db, query=Query().number == story_number, entity_class=Story
        )

    def save_story(self, story: Story) -> Story:
        """Create or update a story"""
        return self.storage.save_entity(
            db=self.story_db, 
            query=Query().number == story.number, 
            entity=story, 
            entity_class=Story
        )

    def update_story(self, story: Story) -> Story:
        """Update an existing story"""
        existing = self.get_story(story.number)
        if not existing:
            raise ValueError(f"Story #{story.number} not found")
        return self.save_story(story)
