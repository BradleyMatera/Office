# Interview Guide

## Thirty-second explanation

During my AWS Support Engineering internship, I built a serverless metadata workflow where an S3 file upload triggered a Lambda function, the function extracted and normalized object metadata, and the result was stored in DynamoDB. I also built a static presentation layer and worked through the cost drivers using measurable inputs such as storage, request counts, Lambda duration, and database reads and writes. The public repository reconstructs that project as a deployable AWS SAM application with tests, security controls, monitoring, and full documentation.

## Two-minute explanation

The problem was to automate metadata handling for uploaded files without managing a long-running server. Amazon S3 acted as the intake layer. An object-created notification invoked a Python Lambda function. The function used the event identity and `HeadObject` data to normalize fields such as the decoded object key, size, content type, ETag, timestamps, version ID, storage class, checksums, and custom user metadata. It stored the result in a DynamoDB table.

For the public implementation, I made the write idempotent using a deterministic record ID and a conditional DynamoDB expression, because asynchronous event systems can deliver the same event more than once. I added an encrypted SQS failure queue after Lambda retries, log retention, an error alarm, encrypted storage, blocked public S3 access, versioning, and point-in-time recovery. The repo uses AWS SAM, unit tests, coverage, linting, and CI validation.

The original internship work was completed in isolated training and project environments, not on production customer systems. The public repo is a recruiter-safe reconstruction that preserves the real architecture and lessons without exposing internal material.

## Likely technical questions

### Why Lambda instead of EC2?

The work is discrete, short-lived, and triggered by an object-created event. Lambda removes idle server cost and patching responsibility while scaling with the event rate.

### Why DynamoDB?

The workflow stores lightweight metadata records with a direct keyed-access pattern. It did not require relational joins or a long-running database server.

### How do you handle duplicate events?

The function derives a deterministic SHA-256 `RecordId` from the bucket, decoded key, version ID, and ETag. It writes with `attribute_not_exists(RecordId)`. A repeated identity is logged as a safe duplicate.

### Why call `HeadObject` when the event already has data?

The S3 notification includes core object information, but `HeadObject` provides the current headers and optional fields used by the normalized record, including content type, storage class, user metadata, checksums, and current version information.

### What happens when processing fails?

Unexpected errors are raised so asynchronous Lambda retry behavior applies. After the configured retries and maximum event age, failed invocations are sent to an encrypted SQS queue for investigation and controlled replay.

### How did you think about cost?

I separated the architecture into measurable drivers: S3 storage and requests, Lambda invocations and duration, DynamoDB reads, writes, storage and recovery, SQS failure traffic, and CloudWatch logs and alarms.

### What would you improve next?

Depending on the requirement, I would add authenticated query APIs, richer observability, SQS buffering for high-volume control, EventBridge for broader routing, Step Functions for multi-stage processing, or a file-content parser for specific formats. I would not add those until the problem required them.

## Claim boundaries

Use these phrases:

- “built during an AWS Support Engineering internship”
- “completed in isolated training and project environments”
- “serverless metadata workflow using S3, Lambda, DynamoDB, and a static frontend layer”
- “created a measurable usage-based cost model”
- “public reconstruction and expansion of the original capstone”

Avoid these claims unless new evidence exists:

- production customer ownership
- live enterprise ticket ownership
- unrestricted administrative access
- direct ownership of Amazon internal systems
- claims that every public source file is the exact original internal file

## Resume bullet

Built an event-driven AWS metadata workflow using S3, Lambda, DynamoDB, and a static frontend layer; added normalized object records, usage-based cost analysis, and a public deployable reconstruction with AWS SAM, idempotent writes, monitoring, tests, and technical documentation.
