"""AWS Lambda handler for the serverless metadata workflow.

The function receives Amazon S3 object-created event notifications, reads the
current object headers, normalizes useful metadata, and writes an idempotent
record to Amazon DynamoDB.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import unquote_plus

import boto3
from botocore.exceptions import ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

_S3_CLIENT = None
_METADATA_TABLE = None


def _get_s3_client():
    global _S3_CLIENT
    if _S3_CLIENT is None:
        _S3_CLIENT = boto3.client("s3")
    return _S3_CLIENT


def _get_metadata_table():
    global _METADATA_TABLE
    if _METADATA_TABLE is None:
        table_name = os.environ.get("TABLE_NAME")
        if not table_name:
            raise RuntimeError("TABLE_NAME environment variable is required")
        _METADATA_TABLE = boto3.resource("dynamodb").Table(table_name)
    return _METADATA_TABLE


def _isoformat(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return str(value)


def _record_id(bucket: str, key: str, version_id: str | None, etag: str | None) -> str:
    identity = "\n".join([bucket, key, version_id or "", etag or ""])
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _validate_event_version(record: dict[str, Any]) -> None:
    version = str(record.get("eventVersion", ""))
    try:
        major = int(version.split(".", maxsplit=1)[0])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid S3 eventVersion: {version!r}") from exc
    if major != 2:
        raise ValueError(f"Unsupported S3 eventVersion major version: {version}")


def _head_object(bucket: str, key: str, version_id: str | None) -> dict[str, Any]:
    request: dict[str, Any] = {"Bucket": bucket, "Key": key}
    if version_id:
        request["VersionId"] = version_id
    return _get_s3_client().head_object(**request)


def _normalize_item(record: dict[str, Any], head: dict[str, Any]) -> dict[str, Any]:
    _validate_event_version(record)

    s3_record = record["s3"]
    bucket = s3_record["bucket"]["name"]
    object_data = s3_record["object"]
    key = unquote_plus(object_data["key"])
    version_id = object_data.get("versionId") or head.get("VersionId")
    etag = str(head.get("ETag") or object_data.get("eTag") or "").strip('"') or None

    item: dict[str, Any] = {
        "RecordId": _record_id(bucket, key, version_id, etag),
        "SchemaVersion": "1",
        "Bucket": bucket,
        "ObjectKey": key,
        "FileName": PurePosixPath(key).name,
        "EventName": record.get("eventName", "unknown"),
        "EventTime": record.get("eventTime", "unknown"),
        "ProcessedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "SizeBytes": Decimal(str(head.get("ContentLength", object_data.get("size", 0)))),
        "ContentType": head.get("ContentType", "application/octet-stream"),
        "ETag": etag or "unknown",
        "LastModified": _isoformat(head.get("LastModified")) or "unknown",
        "StorageClass": head.get("StorageClass", "STANDARD"),
        "Sequencer": object_data.get("sequencer", "unknown"),
        "UserMetadata": head.get("Metadata", {}),
    }

    optional_fields = {
        "VersionId": version_id,
        "CacheControl": head.get("CacheControl"),
        "ContentDisposition": head.get("ContentDisposition"),
        "ContentEncoding": head.get("ContentEncoding"),
        "ContentLanguage": head.get("ContentLanguage"),
        "ChecksumCRC32": head.get("ChecksumCRC32"),
        "ChecksumCRC32C": head.get("ChecksumCRC32C"),
        "ChecksumSHA1": head.get("ChecksumSHA1"),
        "ChecksumSHA256": head.get("ChecksumSHA256"),
    }
    item.update({key_name: value for key_name, value in optional_fields.items() if value is not None})
    return item


def _store_item(item: dict[str, Any]) -> str:
    try:
        _get_metadata_table().put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(RecordId)",
        )
        return "created"
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "ConditionalCheckFailedException":
            LOGGER.info(
                json.dumps(
                    {
                        "message": "Duplicate S3 event ignored",
                        "record_id": item["RecordId"],
                        "bucket": item["Bucket"],
                        "object_key": item["ObjectKey"],
                    }
                )
            )
            return "duplicate"
        raise


def process_record(record: dict[str, Any]) -> dict[str, str]:
    if record.get("eventSource") != "aws:s3":
        raise ValueError(f"Unsupported eventSource: {record.get('eventSource')!r}")

    _validate_event_version(record)
    s3_record = record["s3"]
    bucket = s3_record["bucket"]["name"]
    object_data = s3_record["object"]
    key = unquote_plus(object_data["key"])
    version_id = object_data.get("versionId")

    head = _head_object(bucket, key, version_id)
    item = _normalize_item(record, head)
    status = _store_item(item)

    LOGGER.info(
        json.dumps(
            {
                "message": "S3 metadata record processed",
                "status": status,
                "record_id": item["RecordId"],
                "bucket": bucket,
                "object_key": key,
            }
        )
    )
    return {"record_id": item["RecordId"], "status": status}


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    records = event.get("Records")
    if not isinstance(records, list) or not records:
        raise ValueError("Expected a non-empty S3 Records list")

    results: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []

    for index, record in enumerate(records):
        try:
            results.append(process_record(record))
        except Exception as exc:  # Lambda must retry unexpected processing failures.
            LOGGER.exception("Failed to process S3 record at index %s", index)
            failures.append({"index": str(index), "error": str(exc)})

    if failures:
        raise RuntimeError(json.dumps({"message": "One or more records failed", "failures": failures}))

    return {
        "processed": len(results),
        "results": results,
        "aws_request_id": getattr(context, "aws_request_id", None),
    }
