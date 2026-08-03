# ADR 001: Use an Event-Driven Serverless Architecture

- Status: Accepted
- Date: 2026-08-03 public reconstruction
- Decision scope: Public deployable version of the AWS metadata workflow

## Context

The workflow needs to react when files are uploaded, extract object metadata, store a normalized record, and remain inexpensive when no files are arriving.

A continuously running server would add patching, availability, scaling, and idle-cost responsibilities that are not necessary for this workload.

## Decision

Use:

- Amazon S3 for object intake and event generation
- AWS Lambda for short-lived metadata processing
- Amazon DynamoDB for normalized metadata persistence
- AWS SAM and CloudFormation for repeatable infrastructure deployment
- SQS as the failure destination after asynchronous retries

## Consequences

### Benefits

- no always-on application server
- automatic scaling with object-created events
- clear separation of storage, processing, and persistence
- usage-based cost model
- repeatable deployment and review through infrastructure as code

### Tradeoffs

- asynchronous delivery requires idempotent processing
- distributed failures require logs, alarms, retries, and a failure queue
- local integration testing is less direct than testing a single-process application
- S3 event notifications are not a general workflow orchestrator

## Alternatives considered

### EC2 or a long-running container

Rejected for this use case because the workload is event-driven and intermittent. A server would add operational responsibility without improving the basic workflow.

### Scheduled polling of S3

Rejected because polling adds delay and unnecessary requests. Native S3 event notifications are a better match for object-created processing.

### Relational database

Not selected for the initial workflow because the stored records are lightweight, keyed metadata items without a demonstrated relational-query requirement.

### Step Functions

Not required for the current one-function path. It could become appropriate if the workflow grows into multiple processing stages, approvals, branches, or long-running tasks.

## Review trigger

Revisit this decision if the workflow begins downloading and parsing large file contents, requires complex orchestration, needs relational reporting, or has ordering requirements beyond S3 event notifications.
