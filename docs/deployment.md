# Deployment Guide

## What this deploys

The AWS SAM template creates:

- an encrypted, versioned Amazon S3 upload bucket
- an AWS Lambda metadata extractor
- an encrypted DynamoDB table using on-demand billing
- an encrypted SQS failure queue for events that still fail after retries
- a CloudWatch Logs group with configurable retention
- a CloudWatch alarm for Lambda errors
- the permissions and S3 notification wiring required by the workflow

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

## Validate locally

```bash
make install
make lint
make test
make validate
make build
```

## First deployment

```bash
sam deploy --guided \
  --stack-name aws-serverless-metadata-workflow \
  --region us-east-1
```

Recommended guided answers:

- save arguments to `samconfig.toml`: **yes**
- allow SAM to create IAM roles: **yes**, after reviewing the template
- confirm changes before deploy: **yes**
- disable rollback: **no**

AWS SAM packages the function and deploys the template through AWS CloudFormation.

## Read stack outputs

```bash
make outputs
```

Or:

```bash
aws cloudformation describe-stacks \
  --stack-name aws-serverless-metadata-workflow \
  --query 'Stacks[0].Outputs' \
  --output table
```

Record the values for:

- `UploadBucketName`
- `MetadataTableName`
- `MetadataExtractorFunctionName`
- `FailureQueueUrl`

## Trigger the workflow

Create a harmless sample file:

```bash
printf 'metadata workflow test\n' > sample.txt
```

Upload it:

```bash
aws s3 cp sample.txt s3://YOUR_UPLOAD_BUCKET/incoming/sample.txt \
  --content-type text/plain \
  --metadata source=deployment-guide
```

## Confirm the Lambda ran

```bash
aws logs tail /aws/lambda/YOUR_FUNCTION_NAME --since 10m --follow
```

Look for a structured log entry containing:

- `S3 metadata record processed`
- `status: created`
- the bucket and object key
- the deterministic record ID

## Confirm DynamoDB persistence

For a small test table:

```bash
aws dynamodb scan \
  --table-name YOUR_METADATA_TABLE \
  --max-items 10
```

The stored item should include the bucket, object key, file name, size, content type, ETag, timestamps, storage class, event data, and user metadata.

## Test duplicate safety

Upload the same object again. With bucket versioning enabled, a new object version should produce a separate record. A repeated delivery of the same S3 event identity is ignored by the conditional DynamoDB write and logged as `duplicate`.

## Review failures

Find the failure queue URL from the stack outputs, then inspect it:

```bash
aws sqs receive-message \
  --queue-url YOUR_FAILURE_QUEUE_URL \
  --max-number-of-messages 10 \
  --wait-time-seconds 10
```

Do not delete a failed message until the underlying problem is understood or the event has been safely replayed.

## Update deployment

After changing code or infrastructure:

```bash
sam build
sam deploy
```

If `samconfig.toml` was saved during the guided deployment, SAM reuses the configured stack and region.

## Cleanup warning

The S3 bucket and DynamoDB table use `DeletionPolicy: Retain` so deleting the stack does not silently destroy uploaded files or metadata records.

Delete the stack:

```bash
sam delete --stack-name aws-serverless-metadata-workflow --region us-east-1
```

Then intentionally review and remove retained resources only when their data is no longer needed.
