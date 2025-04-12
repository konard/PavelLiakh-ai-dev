import json
from datetime import date, datetime
from decimal import Decimal
from dataclasses import asdict
from typing import Optional

from deepdiff import DeepDiff
from src.app.service.entities import ERROR_RESPONSE
from tests.helper.file_helper import get_file_content
from src.ioc import storage


def assert_equals_not_strict(expected, actual) -> None:
    assert_equals(
        expected.strip().replace("\n", "").replace("\t", "").replace(" ", ""),
        actual.strip().replace("\n", "").replace("\t", "").replace(" ", ""),
    )


def assert_as_jsons(expected, actual):
    # print(DeepDiff(t1, t2, exclude_paths="root['ingredients']"))  # one item pass it as a string
    expected_json = to_json(expected)
    actual_json = to_json(actual)
    actual_json = remove_empty_fields(actual_json)

    assert_jsons(expected_json, actual_json)


def _check_error_response(actual) -> Optional[str]:
    """Check if response is ERROR_RESPONSE and print related error logs if any"""
    if actual == ERROR_RESPONSE:
        errors = storage.find_errors()
        if errors:
            print("\n=== ERROR LOGS FOUND ===")
            for error in errors:
                print(f"User: {error.user_id}")
                print(f"Message: {error.message}")
                print(f"Error: {error.error}")
                print("---")
            error = "ERROR_RESPONSE received with related error logs (see above)"
            raise AssertionError(error)

    return None


def assert_jsons(expected, actual):
    if isinstance(expected, str):
        expected = json.loads(expected)
    if isinstance(actual, str):
        actual = json.loads(actual)

    result = DeepDiff(expected, actual, ignore_order=True)
    if not result:
        return  # no diff
    else:
        print(f"Expected")
        print(expected)
        if actual:
            actual = json.dumps(actual, ensure_ascii=False)
        print(f"Actual")
        print(f"{actual}")
        raise AssertionError(result)


def assert_equals(expected, actual, replace_expected: bool = False) -> None:
    if expected != actual:
        if not replace_expected:
            _check_error_response(actual)
            raise AssertionError(
                f"Expected not equals actual\nExpected: {expected}\n  Actual: {actual}"
            )
        else:
            # For development purposes. To simplify updating of expecte value in a file
            print(
                f"""\n===\n
                  {actual}
                  \n===\n"""
            )


def to_json(some_object):
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if hasattr(obj, '__module__') and obj.__module__ == 'decimal' and isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    json_params = {"ensure_ascii": False, "indent": 4, "default": json_serial}

    if hasattr(some_object, "as_dict"):
        return json.dumps(some_object.as_dict(), **json_params)

    if isinstance(some_object, dict):
        return json.dumps(some_object, **json_params)

    if isinstance(some_object, list):
        return json.dumps(
            [asdict(item) if not isinstance(item, (str, dict)) else item for item in some_object],
            **json_params,
        )

    if isinstance(some_object, str):
        if some_object.endswith(".json"):
            return get_file_content(some_object)
        else:
            return some_object

    return json.dumps(asdict(some_object), **json_params)


def remove_empty_fields(data):
    """Recursively remove fields with None or null values."""
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v is not None}
    if isinstance(data, str):
        data_as_json = json.loads(data)
        filtered_data = remove_empty_fields(data_as_json)
        return json.dumps(filtered_data)

    return data
