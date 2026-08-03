# Implementation Notes

## Purpose

The workflow turns an S3 object-created event into a normalized DynamoDB metadata record without running an always-on application server or downloading the uploaded file body.

The public repository also turns the original internship capstone into a permanent resume-facing AWS hub with:

- deployable infrastructure
- tested Lambda behavior
- operations and cleanup documentation
- canonical AWS writing teasers
- public proof mapping
- official AWS source verification
- a documented design system
- production static-site validation

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

## Lambda module structure

The public implementation is intentionally small enough to inspect in one file:

```text
src/metadata_extractor/app.py
```

Main responsibilities:

- `_get_s3_client()` — lazily creates and reuses the S3 client
- `_get_metadata_table()` — lazily creates and reuses the DynamoDB table resource
- `_isoformat()` — normalizes timestamps
- `_record_id()` — creates deterministic identity
- `_validate_event_version()` — enforces the supported major version
- `_head_object()` — builds version-aware S3 requests
- `_normalize_item()` — creates the DynamoDB item
- `_store_item()` — performs the conditional write and handles duplicates
- `process_record()` — processes one S3 event record
- `lambda_handler()` — validates the batch, aggregates results, and raises failures

## Lazy AWS SDK clients

The client and table resource are initialized outside the per-record path and cached in module globals.

This allows a warm Lambda execution environment to reuse SDK objects rather than recreating them for every record. The code still treats the execution environment as disposable and does not rely on local state for correctness.

## Event validation

The handler rejects:

- missing or empty `Records`
- non-S3 `eventSource`
- malformed event versions
- unsupported major event versions

The current code accepts S3 event major version `2` and does not assume one exact minor version.

## Object-key decoding

S3 notification keys are URL-encoded. The implementation uses:

```python
unquote_plus(object_data["key"])
```

This converts both percent-encoded path characters and plus signs representing spaces.

## `HeadObject` behavior

The event contains core information, but `HeadObject` supplies the current object headers used by the public data contract.

The request includes:

- bucket
- decoded key
- version ID when present

The implementation does not call `GetObject` and does not download the body.

## Normalized fields

Required public fields include:

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

Optional fields are stored only when available:

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

The design separates:

- repeated delivery of the same event identity
- a replacement upload creating a new object version
- another object with the same filename under a different key or bucket

## Conditional persistence

The function writes with:

```python
ConditionExpression="attribute_not_exists(RecordId)"
```

A `ConditionalCheckFailedException` means the identity is already stored. The function logs `duplicate` and treats the record as successfully handled.

Other DynamoDB exceptions are raised.

## Batch behavior

The Lambda handler iterates through every S3 record in the invocation.

- successful records are stored immediately
- failures are recorded with their record index and error text
- when any record fails, the handler raises one aggregate runtime error

This makes the failure visible to Lambda's asynchronous retry behavior. A retry can revisit records that already succeeded, which is why idempotent persistence is required.

## Structured logging

Successful processing logs JSON containing:

- message
- status
- record ID
- bucket
- object key

Duplicate handling also logs a structured record.

The function does not log object contents or AWS credentials.

## AWS SAM implementation

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
- environment variable for the table
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

## Public Pages implementation

The static site intentionally has no application runtime or AWS credentials.

Public pages:

- `index.html` — primary workflow and resume walkthrough
- `writing.html` — canonical AWS article teasers and DEV editions
- `proof.html` — implementation, repository, credential, and scope evidence
- `sources.html` — official AWS service verification
- `design-system.html` — visible tokens and component contracts
- `404.html` — recovery routes

Shared presentation:

- `styles.css`
- `hub.css`
- first-party SVG architecture and editorial assets
- social preview PNG

Discovery and machine-readable files:

- `robots.txt`
- `sitemap.xml`
- `rss.xml`
- `llms.txt`
- `humans.txt`
- `site.webmanifest`

## Canonical writing implementation

`data/aws-content.json` records the article and repository index used for governance.

Canonical personal article metadata comes from MDX frontmatter in the public blog source repository. The site links to the full articles rather than copying them.

DEV links are treated as secondary distribution versions.

## Static-site validator

`scripts/validate_site.py` uses the Python standard library to validate:

- page structure
- metadata and canonicals
- JSON-LD syntax
- local links and fragments
- image alternatives
- SVG accessibility metadata
- content-index dates and assets
- XML and manifest parsing
- production support files

It does not make external requests. Live availability is handled by a separate scheduled workflow.

## Why the public repository is an expansion

The original capstone architecture centered on:

```text
S3 upload -> Lambda metadata extraction -> DynamoDB storage
```

The public reconstruction adds the engineering work required to make that architecture independently inspectable:

- infrastructure as code
- deterministic identity
- duplicate-event handling
- retries and failure destination
- operational alarms
- data contract
- unit tests and coverage
- CI
- deployment and recovery runbooks
- official-source verification
- production Pages and SEO surface

This expansion is clearly labeled. It does not imply that every public file existed in the exact same form during the internship.
