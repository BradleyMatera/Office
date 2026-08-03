# Metadata Data Contract

## Purpose

The Lambda function converts an S3 object-created notification and the current `HeadObject` response into one normalized DynamoDB item.

The table uses a single partition key:

- `RecordId` — deterministic SHA-256 identifier derived from the bucket, object key, version ID, and ETag

This design makes repeated delivery of the same event safe while allowing distinct object versions to create distinct records.

## Required attributes

| Attribute | Type | Meaning |
|---|---|---|
| `RecordId` | String | Deterministic item identifier and partition key |
| `SchemaVersion` | String | Public data-contract version, currently `1` |
| `Bucket` | String | Source S3 bucket name |
| `ObjectKey` | String | URL-decoded S3 object key |
| `FileName` | String | Final path segment of the object key |
| `EventName` | String | S3 event name such as `ObjectCreated:Put` |
| `EventTime` | String | Timestamp supplied by the S3 notification |
| `ProcessedAt` | String | UTC timestamp when Lambda normalized the record |
| `SizeBytes` | Number | Object size returned by `HeadObject` |
| `ContentType` | String | Object content type or a safe fallback |
| `ETag` | String | Object ETag with surrounding quotes removed |
| `LastModified` | String | UTC ISO-8601 object modification timestamp |
| `StorageClass` | String | S3 storage class, defaulting to `STANDARD` |
| `Sequencer` | String | S3 event sequencer value when supplied |
| `UserMetadata` | Map | Custom S3 user metadata headers |

## Optional attributes

The workflow stores these fields only when S3 supplies them:

- `VersionId`
- `CacheControl`
- `ContentDisposition`
- `ContentEncoding`
- `ContentLanguage`
- `ChecksumCRC32`
- `ChecksumCRC32C`
- `ChecksumSHA1`
- `ChecksumSHA256`

## Example item

```json
{
  "RecordId": "b642d8134b3e...",
  "SchemaVersion": "1",
  "Bucket": "metadata-workflow-uploadbucket-example",
  "ObjectKey": "incoming/quarterly report.pdf",
  "FileName": "quarterly report.pdf",
  "EventName": "ObjectCreated:Put",
  "EventTime": "2026-08-03T18:00:00.000Z",
  "ProcessedAt": "2026-08-03T18:00:01.314Z",
  "SizeBytes": 4096,
  "ContentType": "application/pdf",
  "ETag": "0123456789abcdef0123456789abcdef",
  "LastModified": "2026-08-03T18:00:00Z",
  "StorageClass": "STANDARD",
  "VersionId": "example-version-id",
  "Sequencer": "0066AF001122334455",
  "UserMetadata": {
    "department": "support"
  }
}
```

## Schema evolution

Consumers should check `SchemaVersion` before assuming a field exists. Future versions should add fields without renaming established attributes unless a documented migration is introduced.

## Privacy rule

Custom S3 user metadata becomes part of the DynamoDB record. Do not attach secrets, credentials, protected health information, or unnecessary personal information to uploaded object metadata.
