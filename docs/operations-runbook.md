# Operations Runbook

## Purpose

This runbook covers the deployed AWS metadata workflow, not the static GitHub Pages site. The public site contains documentation and code but has no direct control over AWS resources.

## Normal operating signal

A healthy upload under the configured S3 key prefix produces:

1. an S3 object-created notification
2. one asynchronous Lambda invocation
3. one `HeadObject` request for the referenced object or object version
4. a structured `created` or `duplicate` log entry
5. one normalized DynamoDB item for a new object identity
6. no visible message in the failure queue
7. `OK` state for the Lambda error, Lambda throttle, and failure-queue depth alarms

An object uploaded outside the configured prefix remains in S3 without invoking the extractor. That is expected behavior.

## Operational resources

Record the CloudFormation stack outputs after deployment:

- `UploadBucketName`
- `UploadPrefix`
- `MetadataTableName`
- `MetadataExtractorFunctionName`
- `FailureQueueUrl`
- `AlarmTopicArn`, when an alarm email is configured

Do not rely on manually copied names when the stack outputs are available.

## First checks during an incident

1. Confirm the AWS account and region.
2. Confirm the object exists in the expected bucket, key, and version.
3. Confirm the key starts with the deployed `UploadPrefix`.
4. Check Lambda `Errors`, `Invocations`, `Duration`, and `Throttles`.
5. Review the latest Lambda log stream.
6. Check the SQS failure queue and its visible-message alarm.
7. Confirm the function environment contains the expected `TABLE_NAME`.
8. Confirm the bucket, table, queue, and function still belong to the same CloudFormation stack.
9. Confirm the SNS email subscription is in `Confirmed` state before assuming an alarm email should have arrived.

## Alarm coverage

### Lambda error alarm

Triggers when the function records one or more errors during a five-minute period.

Investigate:

- the exception in the function logs
- IAM access
- object version availability
- DynamoDB table state
- malformed or unexpected event records

### Lambda throttle alarm

Triggers when one or more invocations are throttled during a five-minute period.

Investigate:

- account or function concurrency limits
- an unexpected upload burst
- downstream latency increasing concurrent execution time
- retry traffic caused by another failure

Do not immediately raise concurrency without understanding the source of the traffic and the capacity of downstream services.

### Failure-queue depth alarm

Triggers when one or more messages are visible in the SQS on-failure destination.

A message in this queue means asynchronous processing exhausted the configured retry behavior or otherwise reached the failure destination. Treat it as work requiring investigation, not as a routine queue backlog.

### SNS email path

When `AlarmEmail` is supplied during deployment, CloudFormation creates an SNS topic and requests an email subscription. The recipient must confirm the subscription before email is delivered.

If alarms change state but no email arrives:

- verify the subscription is confirmed
- check spam and quarantine folders
- verify the alarm action references the topic
- verify the email parameter still exists in the deployed stack

## Common failure categories

### Upload does not invoke Lambda

Possible causes:

- the object key is outside the configured prefix
- the event notification was removed or changed
- the upload occurred in another bucket or account
- the retained bucket still points to a function that no longer exists

Action:

- compare the object key with `UploadPrefix`
- inspect the bucket notification configuration
- inspect the stack resources and outputs
- redeploy the stack rather than manually rebuilding the integration

### Access denied on `HeadObject`

Possible causes:

- the event came from a bucket not covered by the function policy
- the object version is not available
- the object uses a customer-managed KMS key the execution role cannot decrypt
- permissions were modified outside CloudFormation

Action:

- verify bucket, key, version, and encryption configuration
- review IAM and KMS permissions
- preserve least privilege rather than adding broad wildcard access
- redeploy the managed stack when configuration drift is responsible

### Access denied on DynamoDB

Possible causes:

- the table was replaced or renamed outside CloudFormation
- `TABLE_NAME` points to the wrong table
- the execution role was modified manually

Action:

- compare stack outputs with the function environment
- inspect CloudFormation drift
- redeploy the SAM stack to restore managed configuration

### Conditional check failure

This is expected for repeated delivery of an already-recorded object identity. The function records it as `duplicate` and treats it as successful idempotent behavior.

Do not change the write to an unconditional `PutItem` merely to remove this log path.

### Unsupported or malformed event

The handler intentionally rejects:

- non-S3 event sources
- empty record lists
- invalid event versions
- unsupported major event versions

Action:

- inspect the failure message
- verify the S3 notification configuration
- preserve validation unless the supported event contract is intentionally expanded and tested

### Lambda timeout

The workflow performs one `HeadObject` call and one conditional DynamoDB write per S3 record. A timeout suggests network, permission, SDK retry, downstream latency, or unusually large multi-record behavior rather than file-content processing.

Action:

- inspect duration and timeout logs
- confirm no code was added that downloads full objects
- review S3 and DynamoDB latency or retry signals
- review the event record count
- change the timeout only after identifying the cause

### DynamoDB item is missing after a successful upload

Check:

- whether the key matched the prefix
- whether the Lambda was invoked
- whether the log outcome was `created`, `duplicate`, or failed
- whether the table name is correct
- whether an item with the deterministic key already exists
- whether the event referenced a different object version than expected

### Unexpected duplicate records

A replacement upload to a versioned bucket normally creates a new version ID and therefore a distinct identity. That is not the same as duplicate delivery of the same event identity.

Compare:

- bucket
- decoded key
- version ID
- ETag
- `RecordId`

## Failure queue handling

Before replaying a failed event:

1. preserve the original queue message and failure context
2. identify the underlying exception
3. correct permissions, configuration, data, or code
4. confirm whether a DynamoDB item already exists
5. verify that the referenced bucket, key, and version still exist
6. replay in a controlled test window
7. confirm the new result in logs and DynamoDB
8. delete the failure message only after recovery is verified

## Replay approaches

### Intentional replacement upload

Copy or upload the object again after the root cause is fixed. With versioning enabled, this normally creates a new version and a new metadata identity.

### Exact event replay

Invoke the function with a reviewed event payload only when the exact referenced object version still exists. This tests idempotency and recovery more precisely, but it must be done intentionally.

Never replay unknown failed events in bulk without checking whether they already produced partial results.

## Monitoring beyond the included alarms

A larger production workload could add:

- SNS integrations beyond email
- Lambda duration percentile alarms
- Lambda concurrent-execution dashboard
- DynamoDB throttled-request alarms
- S3 storage and request dashboards
- log-based metrics for `duplicate` outcomes and failure categories
- queue age alarms
- AWS Cost Anomaly Detection or budget alerts

These are possible extensions, not claims that the current template deploys them.

## Change control

- make infrastructure changes in `template.yaml`
- make function changes in `src/metadata_extractor/app.py`
- add or update tests for behavior changes
- run `make check` before deployment
- review the CloudFormation change set
- avoid manually editing generated roles, event notifications, alarms, or destinations
- update the data contract and increment `SchemaVersion` when compatibility changes
- update the verified-source mapping when a load-bearing service assumption changes
- update the cost model when resources or retention behavior change

## Retained-resource behavior

The S3 bucket and DynamoDB table use retain policies. Stack deletion does not remove them.

### Retained S3 bucket

Because the notification configuration is a property of the retained bucket, inspect it after stack deletion. It may still reference the deleted Lambda function until it is removed or replaced intentionally.

Before reusing or deleting the bucket:

1. inspect all object versions and delete markers
2. inspect the event-notification configuration
3. remove stale function destinations
4. preserve data that still needs retention
5. empty all versions only when deletion is intended

### Retained DynamoDB table

The table and its point-in-time recovery history remain separate from the deleted stack. Record the table name and retention decision before deleting the stack.

Cleanup is an explicit operational task, not an automatic side effect.

## Public-site operations

The GitHub Pages site has its own scheduled health workflow. A failure there does not mean the AWS stack failed, and an AWS alarm does not mean the public site failed.

Use:

- `Validate Serverless Metadata Workflow` for code, site, and SAM checks
- `Monitor GitHub Pages Health` for live public route checks
- CloudWatch and SQS for deployed AWS runtime health
