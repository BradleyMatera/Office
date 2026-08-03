# Cost Model

## Purpose

The project does not publish a single universal monthly price. AWS cost depends on region, account usage, object size, traffic, retries, retention, recovery features, and optional monitoring choices.

The cost model therefore identifies measurable drivers and explains which architectural decisions change them.

## Amazon S3

Cost drivers include:

- bytes stored
- number and size of object versions
- PUT and other write requests
- HEAD and other read requests
- LIST activity used during administration or cleanup
- storage class
- data transfer where applicable
- incomplete multipart-upload behavior before lifecycle cleanup

### Versioning consequence

Replacing an object normally creates another stored version. Versioning improves recovery and event identity but can increase storage until old versions are intentionally expired or removed.

The current template does not automatically expire completed object versions because data-retention policy should be an explicit deployment decision.

## AWS Lambda

Cost drivers include:

- invocation count
- execution duration
- configured memory
- architecture and regional pricing
- asynchronous retries
- additional invocations caused by repeated event delivery
- tracing usage where applicable

The current function reads object headers and performs a database write. It does not download or parse the object body, which keeps the processing path smaller than a content-extraction workflow.

## Amazon DynamoDB

Cost drivers include:

- conditional write requests
- application reads
- administrative scans used for small verification tasks
- stored item size
- point-in-time recovery
- restores and exported data where used

The table uses on-demand billing so the demonstration does not require provisioned-capacity planning. That does not mean every workload is cheapest on on-demand mode.

## Amazon SQS

Cost drivers include:

- failed-event messages
- receive requests during investigation
- delete requests after verified recovery
- message retention

Healthy normal processing should not generate queue traffic. A growing queue is an incident signal and a cost signal.

## Amazon CloudWatch

Cost drivers include:

- log ingestion
- log retention
- custom or detailed metrics when added
- alarm count
- dashboard usage when added
- tracing and related observability features

The repository sets a 14-day default log retention instead of leaving logs indefinitely. The retention period is configurable because operational and compliance needs differ.

The current stack creates alarms for:

- Lambda errors
- Lambda throttles
- visible SQS failure messages

## Amazon SNS

When an alarm email is configured, cost drivers can include:

- published alarm notifications
- delivery type and regional pricing

The recipient must confirm the email subscription. An unconfirmed subscription is not an operational notification path.

## AWS CloudFormation and AWS SAM

CloudFormation and SAM organize deployment, but the resources they create generate the service costs described above.

Build tooling should not be confused with a free runtime architecture.

## GitHub Pages and repository operations

The public site is hosted separately from AWS.

Potential operational considerations include:

- GitHub Pages and Actions plan limits
- workflow minutes for validation and scheduled health checks
- repository storage for source assets
- link-preview and crawler traffic, which does not reach an AWS backend

The current site is static and has no runtime database or AWS API. High reader traffic therefore does not directly create Lambda, DynamoDB, or S3-upload-bucket requests.

## Cost effects of failure and duplication

### Duplicate notification

A duplicate identity still causes:

- a Lambda invocation
- a `HeadObject` request
- a conditional DynamoDB write attempt
- log ingestion

Idempotency protects data correctness. It does not make duplicate delivery costless.

### Function failure

A failing invocation can add:

- retry invocations
- repeated S3 and DynamoDB attempts
- additional log volume
- SQS destination traffic
- alarm state changes and notifications

Operational failures are also cost events.

## Cost effects of retention

The template retains the bucket and table when the stack is deleted.

This reduces accidental data loss but means charges can continue after CloudFormation no longer manages the stack.

A cleanup decision must review:

- S3 object versions and delete markers
- DynamoDB storage and PITR
- retained event-notification configuration
- remaining alarms, queues, topics, or logs managed outside the retained resources

Deleting a stack is not the same thing as confirming that all billable data is gone.

## Measurable inputs

A practical estimate should collect:

### Intake

- uploads per day or month
- average object size
- replacement/version rate
- percentage of uploads under the processing prefix

### Processing

- average Lambda duration
- memory setting
- retry rate
- duplicate-delivery rate
- average number of records per invocation

### Persistence

- average metadata item size
- writes per processed object
- read pattern
- verification scans
- PITR retention setting

### Operations

- daily log volume
- log retention days
- alarm count
- failed-event frequency
- failure-message retention and replay activity
- notification volume

## Cost controls

Possible controls include:

- AWS budgets and cost alerts
- Cost Anomaly Detection
- explicit log retention
- limited event prefixes
- lifecycle policies reviewed against data requirements
- object-version cleanup
- prompt failure investigation
- avoiding unnecessary body downloads
- avoiding repeated scans for normal application access
- intentional deletion of retained resources

These controls have their own setup and governance needs. The repository does not claim that deploying the template automatically configures account-wide budgets or anomaly detection.

## Interview explanation

> I modeled the workflow through measurable service usage rather than calling it free. The main drivers are S3 storage, versions and requests; Lambda invocations, duration and retries; DynamoDB writes, reads, storage and point-in-time recovery; SQS failure traffic; and CloudWatch logs and alarms. The public website is static, so reader traffic does not call the AWS workflow.

## Related material

- [Cost driver diagram](../assets/cost-drivers.svg)
- [Deployment Guide](deployment.md)
- [Operations Runbook](operations-runbook.md)
- [Verified AWS Sources](verified-aws-sources.md)
- [AWS Free Tier: What Actually Costs Money](https://bradleymatera.dev/aws-free-tier-honest-guide/)
