# Deployment Guide

## What this deploys

The AWS SAM template creates:

- an encrypted and versioned Amazon S3 upload bucket
- S3 bucket-owner-enforced ownership with ACLs disabled
- all four S3 Block Public Access controls
- a configurable S3 intake prefix, defaulting to `incoming/`
- an AWS Lambda metadata extractor using Python 3.12 on ARM64
- an encrypted DynamoDB table using on-demand billing
- DynamoDB point-in-time recovery
- an encrypted SQS failure queue for events that still fail after retries
- a CloudWatch Logs group with configurable retention
- CloudWatch alarms for Lambda errors, Lambda throttles, and visible failed events
- an optional SNS topic and email subscription for operational alerts
- the IAM permissions and S3 notification wiring required by the workflow

## Prerequisites

Install and configure:

- Python 3.12
- AWS CLI
- AWS SAM CLI
- Docker, if your SAM build requires a containerized build
- AWS credentials for an account where you are authorized to create the resources

Confirm credentials before deployment:

```bash
aws sts get-caller-identity
```

Review the returned account and ARN before creating resources.

## Validate locally

```bash
make install
make lint
make test
make validate
make build
```

The repository CI also runs Python linting, unit tests with branch coverage, SAM linting, a SAM build, and static-site validation.

## Deployment parameters

| Parameter | Default | Purpose |
|---|---|---|
| `InputPrefix` | `incoming/` | Only object-created events under this key prefix invoke the Lambda function. |
| `LogRetentionDays` | `14` | Controls CloudWatch Logs retention for the function log group. |
| `AlarmEmail` | empty | When supplied, creates an SNS topic and requests an email subscription for operational alarms. |

An empty `AlarmEmail` leaves the CloudWatch alarms in place but does not create the SNS email path.

## First deployment

```bash
sam deploy --guided \
  --stack-name aws-serverless-metadata-workflow \
  --region us-east-1
```

Recommended guided answers:

- `InputPrefix`: keep `incoming/` unless another path is intentional
- `LogRetentionDays`: keep `14` for the demonstration or choose an approved value
- `AlarmEmail`: enter an email you monitor, or leave it empty
- save arguments to `samconfig.toml`: **yes**
- allow SAM to create IAM roles: **yes**, after reviewing the template
- confirm changes before deploy: **yes**
- disable rollback: **no**

AWS SAM packages the function and deploys the template through AWS CloudFormation.

## Confirm the SNS subscription

When `AlarmEmail` is supplied, AWS sends a subscription-confirmation message to that address. Alerts are not delivered until the recipient opens the message and confirms the SNS subscription.

Confirm the subscription before relying on email as an operational signal.

## Read stack outputs

```bash
make outputs
```

Or:

```bash
aws cloudformation describe-stacks \
  --stack-name aws-serverless-metadata-workflow \
  --region us-east-1 \
  --query 'Stacks[0].Outputs' \
  --output table
```

Record the values for:

- `UploadBucketName`
- `UploadPrefix`
- `MetadataTableName`
- `MetadataExtractorFunctionName`
- `FailureQueueUrl`
- `AlarmTopicArn`, when an alarm email was supplied

## Trigger the workflow

Create a harmless sample file:

```bash
printf 'metadata workflow test\n' > sample.txt
```

Upload it under the configured prefix:

```bash
aws s3 cp sample.txt s3://YOUR_UPLOAD_BUCKET/incoming/sample.txt \
  --content-type text/plain \
  --metadata source=deployment-guide
```

An object uploaded outside the configured prefix should remain in S3 without invoking the extractor. That is expected behavior.

## Confirm the Lambda ran

```bash
aws logs tail /aws/lambda/YOUR_FUNCTION_NAME \
  --region us-east-1 \
  --since 10m \
  --follow
```

Look for a structured log entry containing:

- `S3 metadata record processed`
- `status: created`
- the bucket and object key
- the deterministic record ID

The function does not log object contents.

## Confirm DynamoDB persistence

For a small test table:

```bash
aws dynamodb scan \
  --region us-east-1 \
  --table-name YOUR_METADATA_TABLE \
  --max-items 10
```

The stored item should include the bucket, object key, file name, size, content type, ETag, timestamps, storage class, event data, and user metadata.

Do not use a table scan as the normal access pattern for a high-volume production application. It is used here as a direct deployment-verification step for a small demonstration table.

## Test duplicate safety

Bucket versioning means uploading a replacement object normally creates a new version and therefore a separate metadata identity.

To test idempotency itself, replay the same reviewed event identity while the referenced object version still exists. The conditional DynamoDB write should reject the second write and the Lambda should log `duplicate` as a successful outcome.

## Verify alarms

List the stack alarms:

```bash
aws cloudwatch describe-alarms \
  --region us-east-1 \
  --alarm-name-prefix aws-serverless-metadata-workflow
```

CloudFormation-generated physical alarm names may include stack and resource identifiers. You can also inspect the stack resources directly:

```bash
aws cloudformation describe-stack-resources \
  --region us-east-1 \
  --stack-name aws-serverless-metadata-workflow
```

The deployed alarms cover:

- Lambda `Errors`
- Lambda `Throttles`
- SQS `ApproximateNumberOfMessagesVisible` for the failure queue

## Review failed events

Find the failure queue URL from the stack outputs, then inspect it:

```bash
aws sqs receive-message \
  --region us-east-1 \
  --queue-url YOUR_FAILURE_QUEUE_URL \
  --max-number-of-messages 10 \
  --wait-time-seconds 10
```

Do not delete a failed message until the underlying problem is understood or the event has been safely replayed and verified.

See the [Operations Runbook](operations-runbook.md) for the recovery procedure.

## Update deployment

After changing code or infrastructure:

```bash
sam build
sam deploy
```

If `samconfig.toml` was saved during the guided deployment, SAM reuses the configured stack, region, and parameters. Review the generated CloudFormation change set before approving it.

## Rotate or remove the alert email

Run a guided deploy again or update the saved parameter:

```bash
sam deploy --guided
```

- changing `AlarmEmail` requests a new subscription
- setting `AlarmEmail` to an empty value removes the conditional SNS topic from the stack
- the CloudWatch alarms remain even when the SNS path is disabled

## Cleanup warning

The S3 bucket and DynamoDB table use `DeletionPolicy: Retain` and `UpdateReplacePolicy: Retain`. Deleting the stack does not silently destroy uploaded files or metadata records.

Delete the managed stack resources:

```bash
sam delete \
  --stack-name aws-serverless-metadata-workflow \
  --region us-east-1
```

Then intentionally review retained resources before deleting them. A versioned S3 bucket must be emptied of all object versions and delete markers before it can be removed.

Do not automate destructive cleanup in an account containing data that has not been reviewed and backed up.
