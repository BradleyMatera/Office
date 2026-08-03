# Implementation Notes

## Purpose

The workflow turns an Amazon S3 object-created event into a normalized Amazon DynamoDB metadata record without running an always-on application server or downloading the uploaded file body.

The repository contains two connected parts:

1. a deployable AWS SAM implementation of the workflow
2. a static project site that explains the architecture, code, operational behavior, evidence, AWS references, and related writing

## Processing sequence

1. A file is uploaded under the configured S3 key prefix.
2. S3 generates an object-created notification.
3. Lambda receives one or more event records asynchronously.
4. The handler validates the record source and event version.
5. The object key is URL-decoded.
6. The function calls `HeadObject`, including `VersionId` when supplied by the event.
7. Event and object-header fields are normalized into schema version `1`.
8. A deterministic SHA-256 `RecordId` is created.
9. DynamoDB receives a conditional `PutItem`.
10. The function records a structured `created` or `duplicate` outcome.
11. Unexpected failures are raised so Lambda can retry and eventually send the failed invocation to SQS.

## Lambda module

The public implementation is intentionally small enough to inspect in one file:

```text
src/metadata_extractor/app.py
```

Main responsibilities:

- `_get_s3_client()` lazily creates and reuses the S3 client
- `_get_metadata_table()` lazily creates and reuses the DynamoDB table resource
- `_isoformat()` normalizes timestamps
- `_record_id()` creates deterministic identity
- `_validate_event_version()` enforces the supported major version
- `_head_object()` builds version-aware S3 requests
- `_normalize_item()` creates the DynamoDB item
- `_store_item()` performs the conditional write and handles duplicates
- `process_record()` processes one S3 event record
- `lambda_handler()` validates the batch, aggregates results, and raises failures

## AWS SDK client reuse

The S3 client and DynamoDB table resource are initialized outside the per-record path and cached in module globals.

A warm Lambda execution environment can reuse those SDK objects. Correctness does not depend on local state, so a new execution environment can process the same event safely.

## Event validation

The handler rejects:

- missing or empty `Records`
- non-S3 `eventSource`
- malformed event versions
- unsupported major event versions

The code accepts S3 event major version `2` and does not require one exact minor version.

## Object-key decoding

S3 notification keys are URL-encoded. The implementation uses:

```python
unquote_plus(object_data["key"])
```

This converts percent-encoded path characters and plus signs representing spaces.

## `HeadObject`

The S3 event contains core object information, while `HeadObject` supplies the current object headers used by the public data contract.

The request includes:

- bucket
- decoded key
- version ID when present

The function does not call `GetObject` and does not download the body.

## Normalized fields

Required fields include:

- `RecordId`
- `SchemaVersion`
- `Bucket`
- `ObjectKey`
- `FileName`
- `EventName`
- `EventTime`
- `ProcessedAt`
- `SizeBytes`
- `ContentType`
- `ETag`
- `LastModified`
- `StorageClass`
- `Sequencer`
- `UserMetadata`

Optional fields are stored when available:

- `VersionId`
- cache and content-disposition headers
- content encoding and language
- CRC and SHA checksum fields

See [Metadata Data Contract](data-contract.md).

## Deterministic identity

`RecordId` is the SHA-256 digest of a newline-separated identity containing:

```text
bucket
object key
version ID or empty value
ETag or empty value
```

This distinguishes:

- repeated delivery of the same event identity
- a replacement upload that creates a new object version
- another object with the same filename under a different key or bucket

## Conditional persistence

The function writes with:

```python
ConditionExpression="attribute_not_exists(RecordId)"
```

A `ConditionalCheckFailedException` means the identity is already stored. The function logs `duplicate` and treats the record as successfully handled. Other DynamoDB exceptions are raised.

## Batch behavior

The Lambda handler processes every S3 record in the invocation.

- successful records are stored immediately
- failures are recorded with the record index and error text
- when any record fails, the handler raises one aggregate runtime error

A retry can revisit records that already succeeded, which is why idempotent persistence is required.

## Structured logging

Successful and duplicate outcomes log JSON containing:

- message
- status
- record ID
- bucket
- object key

The function does not log object contents or AWS credentials.

## AWS SAM infrastructure

`template.yaml` defines the deployed infrastructure.

### Parameters

- `InputPrefix`, default `incoming/`
- `LogRetentionDays`, default `14`
- optional `AlarmEmail`

### S3

- encryption
- versioning
- bucket-owner-enforced ownership
- public-access blocking
- event prefix filter
- incomplete multipart-upload cleanup
- retained resource behavior

### DynamoDB

- on-demand billing
- encryption
- point-in-time recovery
- retained resource behavior

### Lambda

- Python 3.12 ARM64
- active tracing
- table-name environment variable
- generated S3 and DynamoDB policies
- S3 event notification
- retry and event-age configuration
- SQS on-failure destination

### Operations

- encrypted SQS queue
- log group with explicit retention
- error alarm
- throttle alarm
- failure-queue depth alarm
- optional SNS topic and email subscription

## Public project site

The static site has no application runtime and no AWS credentials.

Public pages:

- `index.html` explains the system, architecture, original internship work, public implementation, reliability, evidence, related writing, and scope
- `writing.html` links to the original AWS and internship articles
- `proof.html` links directly to the code, infrastructure, tests, and operating documents
- `sources.html` connects implementation decisions to official AWS documentation
- `404.html` provides recovery links

Shared interface:

- `styles.css`
- `hub.css`
- Open Sans typography
- Cloudscape-inspired application layout, containers, controls, status indicators, and alerts
- first-party SVG architecture and article artwork
- social-preview PNG

The design system is applied to the pages. There is no public page dedicated to explaining it. Implementation notes are maintained in [Cloudscape Interface Notes](design-system.md).

Discovery and machine-readable files:

- `robots.txt`
- `sitemap.xml`
- `rss.xml`
- `llms.txt`
- `humans.txt`
- `site.webmanifest`

## Article metadata

`data/aws-content.json` records the article and repository index used for consistency checks.

Canonical personal article metadata comes from MDX frontmatter in the public blog repository. The project site links to the complete articles rather than copying them. DEV links are secondary distribution versions.

## Static-site validator

`scripts/validate_site.py` uses the Python standard library to validate:

- page structure
- metadata and canonical URLs
- JSON-LD syntax
- local links and fragments
- image alternatives
- SVG accessibility metadata
- article dates and assets
- XML and manifest parsing
- required production files

The validator does not make external requests. Live availability is checked by a scheduled workflow.

## Original capstone and public expansion

The original capstone architecture centered on:

```text
S3 upload -> Lambda metadata extraction -> DynamoDB storage
```

The public reconstruction adds:

- infrastructure as code
- deterministic identity
- duplicate-event handling
- retries and failure destination
- operational alarms
- data contract
- unit tests and coverage
- CI
- deployment and recovery runbooks
- official AWS references
- the static project site

The public expansion is labeled separately and does not imply that every current repository file existed in the same form during the internship.
