from __future__ import annotations

import importlib
import os
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "metadata_extractor"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("TABLE_NAME", "test-metadata-table")
app = importlib.import_module("app")


class FakeS3Client:
    def __init__(self, response: dict):
        self.response = response
        self.calls: list[dict] = []

    def head_object(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeTable:
    def __init__(self, error_code: str | None = None):
        self.error_code = error_code
        self.items: list[dict] = []

    def put_item(self, **kwargs):
        if self.error_code:
            raise ClientError({"Error": {"Code": self.error_code, "Message": "simulated table error"}}, "PutItem")
        self.items.append(kwargs["Item"])
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}


@pytest.fixture(autouse=True)
def reset_clients(monkeypatch):
    monkeypatch.setattr(app, "_S3_CLIENT", None)
    monkeypatch.setattr(app, "_METADATA_TABLE", None)


@pytest.fixture
def s3_event():
    return {"Records": [{
        "eventVersion": "2.1",
        "eventSource": "aws:s3",
        "eventName": "ObjectCreated:Put",
        "eventTime": "2026-08-03T18:00:00.000Z",
        "s3": {
            "bucket": {"name": "metadata-intake-bucket"},
            "object": {
                "key": "incoming%2Fquarterly+report.pdf",
                "size": 4096,
                "eTag": "event-etag",
                "versionId": "version-1",
                "sequencer": "0066AF001122334455",
            },
        },
    }]}


@pytest.fixture
def head_response():
    return {
        "ContentLength": 4096,
        "ContentType": "application/pdf",
        "ETag": '"head-etag"',
        "LastModified": datetime(2026, 8, 3, 18, 0, tzinfo=UTC),
        "StorageClass": "STANDARD",
        "VersionId": "version-1",
        "Metadata": {"department": "support"},
        "ChecksumSHA256": "checksum-value",
    }


def test_lambda_handler_stores_normalized_metadata(monkeypatch, s3_event, head_response):
    fake_s3 = FakeS3Client(head_response)
    fake_table = FakeTable()
    monkeypatch.setattr(app, "_S3_CLIENT", fake_s3)
    monkeypatch.setattr(app, "_METADATA_TABLE", fake_table)
    result = app.lambda_handler(s3_event, SimpleNamespace(aws_request_id="request-123"))
    assert result["processed"] == 1
    assert result["aws_request_id"] == "request-123"
    assert result["results"][0]["status"] == "created"
    assert fake_s3.calls == [{"Bucket": "metadata-intake-bucket", "Key": "incoming/quarterly report.pdf", "VersionId": "version-1"}]
    stored = fake_table.items[0]
    assert stored["Bucket"] == "metadata-intake-bucket"
    assert stored["ObjectKey"] == "incoming/quarterly report.pdf"
    assert stored["FileName"] == "quarterly report.pdf"
    assert stored["ContentType"] == "application/pdf"
    assert stored["SizeBytes"] == Decimal("4096")
    assert stored["ETag"] == "head-etag"
    assert stored["VersionId"] == "version-1"
    assert stored["UserMetadata"] == {"department": "support"}
    assert stored["ChecksumSHA256"] == "checksum-value"
    assert len(stored["RecordId"]) == 64


def test_duplicate_event_is_safe(monkeypatch, s3_event, head_response):
    monkeypatch.setattr(app, "_S3_CLIENT", FakeS3Client(head_response))
    monkeypatch.setattr(app, "_METADATA_TABLE", FakeTable(error_code="ConditionalCheckFailedException"))
    result = app.lambda_handler(s3_event, SimpleNamespace(aws_request_id="request-duplicate"))
    assert result["processed"] == 1
    assert result["results"][0]["status"] == "duplicate"


def test_unexpected_table_error_is_retried_by_lambda(monkeypatch, s3_event, head_response):
    monkeypatch.setattr(app, "_S3_CLIENT", FakeS3Client(head_response))
    monkeypatch.setattr(app, "_METADATA_TABLE", FakeTable(error_code="AccessDeniedException"))
    with pytest.raises(RuntimeError, match="One or more records failed"):
        app.lambda_handler(s3_event, SimpleNamespace(aws_request_id="request-denied"))


def test_unversioned_object_uses_event_etag_and_default_fields(monkeypatch, s3_event):
    del s3_event["Records"][0]["s3"]["object"]["versionId"]
    fake_s3 = FakeS3Client({"ContentLength": 12, "Metadata": {}})
    fake_table = FakeTable()
    monkeypatch.setattr(app, "_S3_CLIENT", fake_s3)
    monkeypatch.setattr(app, "_METADATA_TABLE", fake_table)
    result = app.lambda_handler(s3_event, None)
    assert result["aws_request_id"] is None
    assert fake_s3.calls == [{"Bucket": "metadata-intake-bucket", "Key": "incoming/quarterly report.pdf"}]
    stored = fake_table.items[0]
    assert stored["ETag"] == "event-etag"
    assert stored["ContentType"] == "application/octet-stream"
    assert stored["StorageClass"] == "STANDARD"
    assert stored["LastModified"] == "unknown"
    assert "VersionId" not in stored


def test_rejects_non_s3_event(monkeypatch, s3_event, head_response):
    s3_event["Records"][0]["eventSource"] = "aws:sns"
    monkeypatch.setattr(app, "_S3_CLIENT", FakeS3Client(head_response))
    monkeypatch.setattr(app, "_METADATA_TABLE", FakeTable())
    with pytest.raises(RuntimeError, match="One or more records failed"):
        app.lambda_handler(s3_event, SimpleNamespace(aws_request_id="request-bad-source"))


def test_rejects_unsupported_event_major_version(monkeypatch, s3_event, head_response):
    s3_event["Records"][0]["eventVersion"] = "3.0"
    monkeypatch.setattr(app, "_S3_CLIENT", FakeS3Client(head_response))
    monkeypatch.setattr(app, "_METADATA_TABLE", FakeTable())
    with pytest.raises(RuntimeError, match="One or more records failed"):
        app.lambda_handler(s3_event, SimpleNamespace(aws_request_id="request-bad-version"))


def test_rejects_invalid_event_version(monkeypatch, s3_event, head_response):
    s3_event["Records"][0]["eventVersion"] = "not-a-version"
    monkeypatch.setattr(app, "_S3_CLIENT", FakeS3Client(head_response))
    monkeypatch.setattr(app, "_METADATA_TABLE", FakeTable())
    with pytest.raises(RuntimeError, match="One or more records failed"):
        app.lambda_handler(s3_event, SimpleNamespace(aws_request_id="request-invalid-version"))


def test_requires_records_list():
    with pytest.raises(ValueError, match="non-empty S3 Records list"):
        app.lambda_handler({}, SimpleNamespace(aws_request_id="request-empty"))


def test_metadata_table_requires_environment_variable(monkeypatch):
    monkeypatch.delenv("TABLE_NAME", raising=False)
    with pytest.raises(RuntimeError, match="TABLE_NAME environment variable is required"):
        app._get_metadata_table()


def test_lazy_clients_are_cached(monkeypatch):
    fake_client = object()
    fake_table = object()
    fake_resource = SimpleNamespace(Table=lambda name: fake_table)
    client_calls: list[str] = []
    resource_calls: list[str] = []
    monkeypatch.setattr(app.boto3, "client", lambda service_name: client_calls.append(service_name) or fake_client)
    monkeypatch.setattr(app.boto3, "resource", lambda service_name: resource_calls.append(service_name) or fake_resource)
    assert app._get_s3_client() is fake_client
    assert app._get_s3_client() is fake_client
    assert app._get_metadata_table() is fake_table
    assert app._get_metadata_table() is fake_table
    assert client_calls == ["s3"]
    assert resource_calls == ["dynamodb"]


def test_isoformat_supports_none_and_plain_values():
    assert app._isoformat(None) is None
    assert app._isoformat("already-formatted") == "already-formatted"
