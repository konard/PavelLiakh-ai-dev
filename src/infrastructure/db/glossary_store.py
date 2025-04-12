import json
from typing import Dict, List, Optional
from src.config import Config


class GlossaryStore:
    def __init__(self):
        self.config = Config()
        self.glossary = self._load_glossary()

    def _load_glossary(self) -> Dict:
        """Load glossary data from JSON file."""
        glossary_path = self.config.get_resource("files/glossary.json")
        with open(glossary_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_terms(self) -> List[str]:
        """Get list of all glossary terms excluding section headers."""
        return [term for term in self.glossary.keys() if not term.startswith("//")]

    def get_term_definition(self, term: str) -> Optional[Dict]:
        return self.glossary.get(term)

    def get_terms_definitions(self, terms: List[str]) -> Dict[str, Dict]:
        return {term: self.glossary.get(term) for term in terms}

    def get_terms_by_topics(self, topics: List[str]) -> List[str]:
        if not topics:
            return []

        lower_topics = [topic.lower() for topic in topics]
        return [
            term
            for term in self.get_all_terms()
            if any(topic in term.lower() for topic in lower_topics)
        ]

    def get_formatted_glossary_text(self, topics: List[str]) -> str:
        relevant_terms = self.get_terms_by_topics(topics)
        definitions = self.get_terms_definitions(relevant_terms)

        return (
            json.dumps(self.get_terms_definitions(relevant_terms), ensure_ascii=False)
            if definitions
            else ""
        )
