import requests_mock
import unittest
from src.infrastructure.telegram.file_downloader import download_file
from unittest.mock import patch


class TestAnalyzeTask(unittest.TestCase):
    @patch("src.config.Config.is_test", return_value=False)
    def test_download_file(self, mock_is_test):
        file_id = "test_file_id"
        bot_token = "test_token"

        # Mock the URLs
        file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        download_url = f"https://api.telegram.org/file/bot{bot_token}/filedownloadpath_file.csv"

        with requests_mock.Mocker() as m:
            # Mock the getFile response
            m.get(
                file_info_url,
                json={
                    "ok": True,
                    "result": {
                        "file_path": "filedownloadpath_file.csv",
                        "file_size": 12345,
                    },
                },
            )

            # Mock the file download response
            m.get(download_url, content=b"file content here")

            # Call the function
            user_file = download_file(file_id, bot_token)

            # Assertions
            self.assertIsNotNone(user_file)
            self.assertEqual(
                user_file.original_filename, "filedownloadpath_file.csv"
            )  # From the mocked file_path
            self.assertEqual(user_file.original_url, download_url)  # Should match the download URL
            self.assertEqual(user_file.size, 12345)  # From the mocked file_size

            # Assert that requests were made
            assert m.called
            assert m.request_history[0].method == "GET"
            assert m.request_history[0].url == file_info_url
            assert m.request_history[1].url == download_url


if __name__ == "__main__":
    unittest.main()
