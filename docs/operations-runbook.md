# Operations Runbook

## Normal operating signal

A healthy upload produces:

1. an S3 object-created notification
2. one Lambda invocation
3. a structured `created` or `duplicate` log entry
4. one normalized DynamoDB item for a new object identity
5. no message in the failure queue

## First checks during an incident

1. Confirm the object exists in the expected bucket and key.
2. Check the Lambda `Errors`, `Invocations`, `Duration`, and `Throttles` metrics.
3. Review the latest Lambda log stream.
4. Check the SQS failure queue.
5. Confirm the function environment contains the expected `TABLE_NAME`.
6. Confirm the table and bucket still exist and are in the same deployed account and region.

## Common failure categories

### Access denied on `HeadObject`

Possible causes:

- the event came from a bucket not covered by the function policy
- the object uses a KMS key the function cannot decrypt
- the object version is not available

Action:

- verify the bucket and object identity
- review IAM and KMS permissions
- keep least privilege rather than adding broad wildcard access

### Access denied on DynamoDB

Possible causes:

- the table was replaced or renamed outside CloudFormation
- the environment variable points to the wrong table
- the execution role was modified manually

Action:

- compare deployed stack outputs with the function environment
- redeploy the SAM stack to restore managed configuration

### Conditional check failure

This is expected for a repeated delivery of an already-recorded object identity. The function records it as `duplicate` and treats it as successful idempotent behavior.

### Unsupported or malformed event

The handler intentionally rejects non-S3 events, empty record lists, and unsupported major event versions.

Action:

- inspect the failure message
- verify the S3 notification configuration
- do not weaken validation just to silence an unexpected event source

### Lambda timeout

The workflow performs one `HeadObject` call and one DynamoDB conditional write per S3 record. A timeout suggests network, permission, SDK retry, or unusually large multi-record-event behavior rather than file-content processing.

Action:

- inspect duration and timeout logs
- confirm no unexpected code was added that downloads entire files
- review downstream service latency

## Failure queue handling

The function uses asynchronous retry settings and an encrypted SQS on-failure destination.

Before replaying a message:

1. identify and correct the root cause
2. confirm whether the DynamoDB item already exists
3. preserve the original failure details
4. replay in a controlled test window
5. confirm the new result in logs and DynamoDB
6. delete the failure message only after successful recovery

## Replay approach

The safest replay is normally to copy or re-upload the object intentionally after the root cause is fixed. For an exact event replay, invoke the function with a reviewed event payload only when the referenced bucket, key, and version still exist.

## Monitoring recommendations

The template includes a basic Lambda error alarm. A fuller operational deployment could add:

- alarm notifications through SNS
- SQS failure-queue depth alarm
- Lambda throttles alarm
- duration percentile dashboard
- DynamoDB throttled-request alarm
- S3 request and storage dashboard
- log-based metric filters for `duplicate` and processing failures

## Change control

- make infrastructure changes in `template.yaml`
- validate and build before deployment
- review the CloudFormation change set
- avoid manually editing generated Lambda roles or S3 notifications
- document schema changes and increment `SchemaVersion` when compatibility changes

## Data protection

The bucket and table use retention policies in the template. Stack deletion does not automatically remove them. Cleanup must be an explicit, reviewed action.
