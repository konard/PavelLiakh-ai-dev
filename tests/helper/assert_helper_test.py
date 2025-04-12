import unittest

from tests.helper.assert_helper import assert_as_jsons, assert_equals


class TestAssertHelper(unittest.TestCase):
    def test_assert_jsons(self):
        json1 = {"name": "Alice", "age": 25, "skills": ["Python", "Django"]}
        json2 = {"skills": ["Python", "Django"], "age": 25, "name": "Alice"}
        assert_as_jsons(json1, json2)

    def test_assert_different_jsons(self):
        json1 = {"name": "Alice"}
        json2 = {"skills": ["Python", "Django"], "age": 25, "name": "Alice"}
        try:
            assert_as_jsons(json1, json2)
        except AssertionError as e:
            assert_equals(
                e.__str__(), "{'dictionary_item_added': [\"root['skills']\", \"root['age']\"]}"
            )
            return
        raise AssertionError("Expected AssertionError")


if __name__ == "__main__":
    unittest.main()
