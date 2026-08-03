# Architecture

## Overview

The AWS Serverless Metadata Workflow is an event-driven system built around seven responsibilities:

1. **Private object intake** — accept uploaded files under a controlled S3 key prefix
2. **Event generation** — react to object-created notifications
3. **Metadata processing** — validate the event and read current object headers
4. **Normalization and identity** — create a versioned item with deterministic identity
5. **Idempotent persistence** — store new records without duplicating repeated event delivery
6. **Failure and operational handling** — retry unexpected failures, quarantine exhausted events, and expose alarms
7. **Public explanation** — present the architecture, proof, writing, and official-source validation without exposing an AWS account

## Deployed AWS path

```text
Object upload under InputPrefix
               |
               v
          Amazon S3
               |
     ObjectCreated notification
               v
          AWS Lambda
               |
     validate event contract
               |
     version-aware HeadObject
               |
      normalize metadata
               |
 deterministic SHA-256 identity
               |
 conditional DynamoDB PutItem
               v
       Amazon DynamoDB
```

Unexpected asynchronous processing failures follow a separate path:

```text
Lambda failure
     |
maximum event age and retries
     |
     v
Encrypted SQS failure destination
     |
CloudWatch queue-depth alarm
     |
Optional confirmed SNS email subscription
```

## Amazon S3 intake layer

The S3 bucket provides:

- server-side encryption
- versioning
- bucket-owner-enforced ownership with ACLs disabled
- all four Block Public Access controls
- a configurable event-notification prefix, defaulting to `incoming/`
- incomplete multipart-upload cleanup
- retained-data behavior during stack deletion

The prefix narrows the event source without pretending it is an authorization boundary. IAM and bucket policies remain responsible for access control.

## AWS Lambda processing layer

The Lambda function:

- uses Python 3.12 on ARM64
- validates that the event source is S3
- validates the event major version
- URL-decodes the object key
- sends the version ID to `HeadObject` when available
- reads object headers without downloading the body
- normalizes required and optional fields
- creates deterministic record identity
- performs a conditional DynamoDB write
- logs structured outcomes
- raises unexpected failures for asynchronous retry

The function does not parse file contents. Adding content extraction would change the cost, security, memory, timeout, test, and data-classification requirements.

## DynamoDB persistence layer

The table uses:

- `RecordId` as the partition key
- on-demand billing
- encryption at rest
- point-in-time recovery
- retain policies

`RecordId` is a SHA-256 hash of:

- bucket
- decoded object key
- version ID when present
- ETag

The conditional expression:

```text
attribute_not_exists(RecordId)
```

prevents repeated delivery of the same identity from replacing or duplicating an existing item.

## Failure handling

The Lambda asynchronous configuration uses:

- maximum event age of 3,600 seconds
- two retry attempts
- encrypted SQS on-failure destination

The failure queue is not a normal work queue. It contains events requiring investigation after retry behavior is exhausted.

## Observability and notifications

The stack creates:

- a dedicated Lambda log group
- configurable log retention, defaulting to 14 days
- Lambda error alarm
- Lambda throttle alarm
- SQS visible-message alarm for failed events
- optional SNS email notification path

Email delivery requires the recipient to confirm the SNS subscription.

The alarms provide an initial signal. They do not replace dashboards, cost monitoring, request tracing, or a broader operational strategy for a larger workload.

## IAM model

AWS SAM policy templates grant the function read access to the generated S3 bucket and read/write access to the generated DynamoDB table.

The S3 policy supports versioned-object reads, which is required when an event references a specific version.

The public GitHub Pages site has no AWS credentials and no runtime connection to these resources.

## Public documentation architecture

GitHub Pages serves a separate static content system:

- primary workflow walkthrough
- AWS writing hub
- proof map
- verified official AWS source page
- design-system page
- documentation library
- machine-readable metadata, RSS, sitemap, and `llms.txt`

This separation is deliberate:

- the public site remains safe to crawl and share
- a private AWS deployment remains under the deployer's account controls
- the walkthrough can explain the real design without exposing buckets, account IDs, object contents, or credentials

![Security boundary](../assets/security-boundary.svg)

## Why this architecture fits the problem

- **Event-driven:** processing starts when an object arrives under the configured prefix.
- **Serverless:** no always-on application server is required.
- **Idempotent:** repeated event delivery is an expected condition, not an accidental overwrite.
- **Observable:** errors, throttles, logs, and failed-event backlog have defined signals.
- **Recoverable:** DynamoDB PITR, retained resources, retries, and a failure queue provide recovery options.
- **Cost-aware:** each managed service has measurable usage and retention drivers.
- **Public-safe:** the documentation and the AWS account are separate systems.
- **Auditable:** code, tests, data contract, runbook, proof, and official sources are independently accessible.

## Architectural tradeoffs

### Direct S3-to-Lambda notification

This keeps the current path simple but does not provide buffering, broad event routing, or ordering guarantees.

A larger system might insert SQS or EventBridge between S3 and processing, depending on throughput, routing, replay, and isolation requirements.

### One DynamoDB partition key

The current design is appropriate for direct record identity and demonstration queries. It is not presented as a complete analytics model.

Additional access patterns could require secondary indexes, export, streams, or a separate reporting store.

### Retained resources

Retention reduces accidental data loss but creates an explicit cleanup responsibility. A retained bucket may preserve an event-notification configuration after stack deletion and must be inspected before reuse.

### GitHub Pages

Static hosting is fast, resilient, and easy to share, but it cannot display live AWS records without introducing an authenticated API and a new security model. The current site intentionally avoids exposing a live backend.

## Diagrams

- [Architecture overview](../assets/architecture-overview.svg)
- [Processing flow](../assets/processing-flow.svg)
- [Data model](../assets/data-model.svg)
- [Security boundary](../assets/security-boundary.svg)
- [Cost drivers](../assets/cost-drivers.svg)

## Related documents

- [Architecture Decision Record](architecture-decisions/001-event-driven-serverless.md)
- [Implementation Notes](implementation-notes.md)
- [Data Contract](data-contract.md)
- [Operations Runbook](operations-runbook.md)
- [Verified AWS Sources](verified-aws-sources.md)
