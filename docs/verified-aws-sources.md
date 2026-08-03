# Verified AWS Sources

Last reviewed: **August 3, 2026**

This document maps the important implementation claims in the public AWS Serverless Metadata Workflow to current, official AWS documentation. It is not meant to replace the AWS docs. It shows why each design choice in this repository is technically legitimate and where to verify it.

## Verification summary

| Repository behavior | Official AWS behavior | Implementation |
|---|---|---|
| S3 may deliver a notification more than once | S3 Event Notifications are designed for at-least-once delivery and rare duplicate notifications can occur | Deterministic `RecordId` plus a conditional DynamoDB write |
| S3 notifications can arrive out of order | AWS does not guarantee event-notification ordering | The item records the S3 `sequencer`; the current workflow does not claim global ordering |
| Object headers can be read without downloading the file body | `HeadObject` returns object metadata and no response body | Lambda calls `head_object` and does not download object content |
| Asynchronous Lambda failures can be retried and sent to a destination | Lambda supports maximum event age, 0–2 retries, and on-failure destinations | AWS SAM `EventInvokeConfig` uses a one-hour maximum age, two retries, and an SQS destination |
| A DynamoDB put can be made conditional | `attribute_not_exists(partitionKey)` prevents replacement when the key already exists | `ConditionExpression="attribute_not_exists(RecordId)"` |
| S3 public access can be blocked at the bucket level | S3 provides four Block Public Access settings and recommends enabling all four | All four settings are enabled in `template.yaml` |
| ACLs can be disabled with bucket-owner enforcement | `BucketOwnerEnforced` disables ACLs and makes policy-based access the control plane | `OwnershipControls` explicitly selects `BucketOwnerEnforced` |
| DynamoDB can maintain continuous recovery points | Point-in-time recovery provides managed continuous backups and up to 35 days of recovery points | PITR is enabled on the metadata table |
| CloudWatch log retention is configurable | A log-group retention policy controls how long log events are retained | The template accepts a configurable retention period, defaulting to 14 days |
| CloudWatch alarms can notify through SNS | CloudWatch alarm actions can publish notifications to an SNS topic | An optional email parameter creates an SNS topic and connects alarm actions |

## 1. Amazon S3 event delivery, duplicates, and ordering

### Official documentation

- [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html)
- [Event notification types and destinations](https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-how-to-event-types-and-destinations.html)
- [Event message structure](https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-content-structure.html)

### Verified behavior

AWS documents S3 Event Notifications as at-least-once delivery. Notifications are not guaranteed to arrive in event order, and duplicate notifications can occur. The `sequencer` can help compare events for the same object key, but it cannot establish ordering across different keys.

### Repository response

The function creates a deterministic SHA-256 `RecordId` from the bucket, decoded key, version ID, and ETag. The DynamoDB write uses a condition expression, so a repeated event identity is logged as `duplicate` rather than stored twice.

The current schema also records the S3 `Sequencer`. The workflow does not pretend that this creates a total order across an entire bucket.

## 2. Amazon S3 `HeadObject`

### Official documentation

- [`HeadObject` API reference](https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadObject.html)

### Verified behavior

AWS documents `HeadObject` as retrieving object metadata without returning the object itself. The response has no body. The caller needs the relevant object-read permission, and version-aware requests may require the corresponding object-version permission.

### Repository response

The Lambda function uses `head_object` to collect current headers and optional checksum fields. It does not download or parse the complete file body.

## 3. AWS Lambda asynchronous retries and destinations

### Official documentation

- [Configuring error handling for asynchronous invocations](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-configuring.html)
- [`FunctionEventInvokeConfig` API reference](https://docs.aws.amazon.com/lambda/latest/api/API_FunctionEventInvokeConfig.html)
- [AWS SAM `EventInvokeConfiguration`](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-property-function-eventinvokeconfiguration.html)

### Verified behavior

Lambda supports a maximum event age and a configurable retry count from zero through two for function errors. It also supports destinations for events after processing. A standard SQS queue is a supported on-failure destination.

### Repository response

The SAM template sets:

```yaml
EventInvokeConfig:
  MaximumEventAgeInSeconds: 3600
  MaximumRetryAttempts: 2
  DestinationConfig:
    OnFailure:
      Type: SQS
      Destination: !GetAtt FailureQueue.Arn
```

Unexpected processing errors are raised so Lambda can apply this asynchronous retry and failure-destination behavior.

## 4. DynamoDB conditional writes

### Official documentation

- [DynamoDB condition-expression examples](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html)
- [`PutItem` API reference](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_PutItem.html)

### Verified behavior

A normal `PutItem` can replace an existing item with the same primary key. AWS recommends using a condition expression containing `attribute_not_exists` when a put must only succeed if that key is not already present.

### Repository response

```python
metadata_table.put_item(
    Item=item,
    ConditionExpression="attribute_not_exists(RecordId)",
)
```

A `ConditionalCheckFailedException` is interpreted as an already-processed event identity, not as a new processing failure.

## 5. S3 public access and object ownership

### Official documentation

- [Blocking public access to S3 storage](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- [Configuring Block Public Access for a bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/configuring-block-public-access-bucket.html)
- [S3 Object Ownership and disabled ACLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html)

### Verified behavior

S3 provides four Block Public Access controls and recommends enabling all four where public access is not required. `BucketOwnerEnforced` disables ACLs and shifts access control to policies.

### Repository response

The upload bucket enables all four Block Public Access settings and explicitly uses bucket-owner-enforced ownership controls. The public GitHub Pages site is separate from this private upload bucket.

## 6. DynamoDB point-in-time recovery

### Official documentation

- [Point-in-time backups for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Point-in-time-recovery.html)

### Verified behavior

DynamoDB point-in-time recovery provides managed continuous backups and recovery points at per-second granularity for a configurable recovery window up to 35 days. Restoring creates a new table.

### Repository response

PITR is enabled on the metadata table to provide a recovery path from accidental writes or deletes. The feature has a cost and is documented as a cost driver rather than described as free.

## 7. CloudWatch Logs retention

### Official documentation

- [`PutRetentionPolicy` API reference](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutRetentionPolicy.html)

### Verified behavior

CloudWatch Logs supports an explicit retention period for log events. Expired events are marked for deletion and may take additional time to be physically removed.

### Repository response

The template creates the Lambda log group with a configurable `RetentionInDays` value. The default is 14 days, preventing indefinite log retention by accident.

## 8. CloudWatch alarms and SNS email notifications

### Official documentation

- [Using CloudWatch alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Alarms.html)
- [`AWS::SNS::Topic` CloudFormation reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-sns-topic.html)
- [`AWS::SNS::Topic` subscription property](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-sns-topic-subscription.html)

### Verified behavior

CloudWatch alarm actions can publish to SNS. An email subscription must be confirmed by the recipient before messages are delivered.

### Repository response

The template accepts an optional `AlarmEmail`. When supplied, CloudFormation creates an SNS topic, requests an email subscription, and connects the Lambda error, Lambda throttle, and failure-queue alarms to the topic.

## 9. What this verification does not prove

Official service documentation confirms that the architecture and implementation patterns are supported by AWS. It does not prove that the public repository is a copy of internal Amazon source code, that the internship involved production customer ownership, or that a deployed stack is currently running in Bradley Matera's AWS account.

The repository remains a public reconstruction and expansion of the original internship capstone.
