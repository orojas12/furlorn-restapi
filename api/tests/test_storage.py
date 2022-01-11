from io import BytesIO
import os
from unittest.mock import Mock, patch
from uuid import UUID, uuid4
from django.conf import settings

from django.core.files.base import File

from api.storage import S3Storage
from botocore.exceptions import ClientError
from django.test import TestCase


@patch("api.storage.bucket.Object", spec=True)
class TestS3Storage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.response_not_found = {"ResponseMetadata": {"HTTPStatusCode": 404}}
        cls.response_ok = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def test_get_unique_name_returns_uuid_with_ext(self, _):
        name = S3Storage().get_unique_name("dog.jpg")
        root, ext = os.path.splitext(name)
        self.assertIsInstance(UUID(root), UUID)
        self.assertEqual(ext, ".jpg")

    @patch("api.storage.S3Storage.exists")
    @patch("api.storage.S3Storage.get_unique_name")
    def test_get_available_name_returns_unique_name(
        self, mock_get_unique_name, mock_exists, _
    ):
        mock_exists.return_value = False
        mock_get_unique_name.return_value = "unique.jpg"
        available_name = S3Storage().get_available_name("test.jpg")
        self.assertEqual(available_name, "unique.jpg")

    def test_exists_returns_true_if_200(self, mock_obj):
        mock_obj.return_value = Mock(load=Mock(return_value=self.response_ok))
        self.assertTrue(S3Storage().exists("test"))

    def test_exists_returns_false_if_404(self, mock_obj):
        mock_obj.return_value = Mock(
            load=Mock(side_effect=ClientError(self.response_not_found, "mock"))
        )
        self.assertFalse(S3Storage().exists("test"))

    def test_save_returns_filename(self, _):
        name = str(uuid4()) + ".jpg"
        filename = S3Storage()._save(name, File(BytesIO(b"content")))
        self.assertEqual(filename, name)

    @patch("api.storage.bucket", spec=True)
    def test_save_uploads_to_s3(self, mock_bucket, _):
        put_object = Mock(return_value=self.response_ok)
        mock_bucket.put_object = put_object
        storage = S3Storage()
        self.assertEqual(
            storage._save("name.jpg", File(BytesIO(b"content"))), "name.jpg"
        )
        self.assertTrue(put_object.called)

    @patch("api.storage.client", spec=True)
    def test_url_calls_generate_presigned_url_correctly(self, mock_client, _):
        mock_generate_presigned_url = Mock()
        mock_client.generate_presigned_url = mock_generate_presigned_url
        storage = S3Storage()
        _ = storage.url("name")
        mock_generate_presigned_url.assert_called_once_with(
            ClientMethod="get_object",
            Params={"Bucket": settings.S3_STORAGE["BUCKET_NAME"], "Key": "name"},
            ExpiresIn=60,
        )

    @patch("api.storage.client", spec=True)
    def test_url_returns_none_on_error(self, mock_client, _):
        mock_generate_presigned_url = Mock(
            side_effect=ClientError(
                error_response=self.response_not_found, operation_name="mock"
            )
        )
        mock_client.generate_presigned_url = mock_generate_presigned_url
        storage = S3Storage()
        url = storage.url("name")
        self.assertEqual(url, None)

    def test_delete_calls_object_delete_once(self, mock_obj):
        mock_delete = Mock()
        mock_obj.return_value = Mock(delete=mock_delete)
        storage = S3Storage()
        storage.delete("name")
        mock_delete.assert_called_once()
