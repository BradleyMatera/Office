# AWS Serverless Metadata Workflow

[![Validate Serverless Metadata Workflow](https://github.com/BradleyMatera/Office/actions/workflows/validate.yml/badge.svg)](https://github.com/BradleyMatera/Office/actions/workflows/validate.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-1f883d)](https://bradleymatera.github.io/Office/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A deployable, tested, and fully documented public reconstruction of the AWS serverless metadata workflow I built during my AWS Support Engineering internship.

**Live case study:** https://bradleymatera.github.io/Office/  
**Recruiter portfolio:** https://bradleymatera.dev/recruiter/

![AWS Serverless Metadata Workflow architecture](assets/architecture-overview.svg)

## What the system does

1. A file is uploaded to an encrypted, versioned Amazon S3 bucket.
2. S3 sends an object-created notification to AWS Lambda.
3. The Python function URL-decodes the key and calls `HeadObject`.
4. It normalizes object metadata into a versioned data contract.
5. It creates a deterministic SHA-256 record ID.
6. It writes the item to DynamoDB with an idempotent conditional expression.
7. Unexpected failures are retried and then sent to an encrypted SQS failure queue.
8. CloudWatch logs and an error alarm provide the initial operational signal.

The current implementation reads object headers. It does **not** download or parse the entire file body.

## Why this repository exists

The original project was completed in isolated AWS internship training and project environments without production customer data. This public repository preserves the real architecture and engineering story while intentionally excluding confidential or internal-only material.

The repo is both:

- a recruiter-safe technical case study
- a real AWS SAM application that an authorized user can validate, test, build, and deploy

## What is implemented

### Infrastructure as code

- AWS SAM and CloudFormation
- encrypted S3 upload bucket
- S3 public access blocked
- S3 versioning
- incomplete multipart-upload cleanup
- Python 3.12 ARM64 Lambda
- least-privilege SAM policy templates
- DynamoDB on-demand billing
- DynamoDB encryption and point-in-time recovery
- asynchronous retry limits
- encrypted SQS failure queue
- CloudWatch Logs retention
- Lambda error alarm
- retained S3 and DynamoDB data during stack deletion

### Lambda behavior

- S3 event-version validation
- non-S3 event rejection
- URL-decoded object keys
- version-aware `HeadObject` requests
- normalized metadata fields
- deterministic record identity
- idempotent conditional writes
- duplicate-event handling
- structured JSON logs
- multi-record error aggregation
- failure propagation for Lambda retries

### Verification

- pytest unit tests
- branch coverage enforcement
- Ruff linting
- AWS SAM template linting
- AWS SAM build verification
- GitHub Actions CI on pushes and pull requests

### Public documentation

- GitHub Pages site
- architecture diagram
- processing sequence diagram
- simplified data model
- security-boundary diagram
- cost-driver diagram
- deployment guide
- metadata data contract
- operations runbook
- troubleshooting guide
- accessibility notes
- project history
- interview guide
- architecture decision record
- security and contribution policies

## Architecture

![Architecture overview](assets/architecture-overview.svg)

```text
File upload
    |
    v
Amazon S3 -- ObjectCreated event --> AWS Lambda
                                         |
                                         | HeadObject + normalization
                                         v
                                  Amazon DynamoDB
                                         |
                         logs, errors, retries, failure queue
```

The public GitHub Pages site is separate from the private AWS deployment. It contains documentation, code, examples, and diagrams, but no AWS credentials and no direct access to uploaded objects.

![Security boundary](assets/security-boundary.svg)

## Normalized metadata record

The DynamoDB partition key is `RecordId`, a deterministic SHA-256 hash derived from:

- bucket name
- decoded object key
- object version ID, when present
- ETag

Representative fields include:

```json
{
  "RecordId": "b642d8134b3e...",
  "SchemaVersion": "1",
  "Bucket": "metadata-workflow-uploadbucket-example",
  "ObjectKey": "incoming/quarterly report.pdf",
  "FileName": "quarterly report.pdf",
  "EventName": "ObjectCreated:Put",
  "EventTime": "2026-08-03T18:00:00.000Z",
  "ProcessedAt": "2026-08-03T18:00:01.314Z",
  "SizeBytes": 4096,
  "ContentType": "application/pdf",
  "ETag": "0123456789abcdef0123456789abcdef",
  "LastModified": "2026-08-03T18:00:00Z",
  "StorageClass": "STANDARD",
  "VersionId": "example-version-id",
  "Sequencer": "0066AF001122334455",
  "UserMetadata": {
    "department": "support"
  }
}
```

See [the complete data contract](docs/data-contract.md).

## Quick start

### Prerequisites

- Python 3.12
- AWS CLI
- AWS SAM CLI
- Docker when a containerized SAM build is required
- authorized AWS credentials

### Run local checks

```bash
make install
make lint
make test
make validate
make build
```

### Deploy

```bash
sam deploy --guided \
  --stack-name aws-serverless-metadata-workflow \
  --region us-east-1
```

### Read outputs

```bash
make outputs
```

### Trigger the workflow

```bash
printf 'metadata workflow test\n' > sample.txt

aws s3 cp sample.txt s3://YOUR_UPLOAD_BUCKET/incoming/sample.txt \
  --content-type text/plain \
  --metadata source=readme
```

### Verify processing

```bash
aws logs tail /aws/lambda/YOUR_FUNCTION_NAME --since 10m --follow

aws dynamodb scan \
  --table-name YOUR_METADATA_TABLE \
  --max-items 10
```

Read the [full deployment guide](docs/deployment.md) before creating or deleting resources.

## Reliability model

### Idempotency

S3 and other asynchronous systems can deliver the same event more than once. The function uses a deterministic record ID and:

```text
ConditionExpression = attribute_not_exists(RecordId)
```

A repeated identity returns `duplicate` instead of creating another item.

### Retries and failed events

The SAM template configures:

- maximum event age: 3,600 seconds
- maximum retry attempts: 2
- encrypted SQS on-failure destination

The [operations runbook](docs/operations-runbook.md) explains investigation and replay.

### Data protection

- S3 encryption at rest
- DynamoDB encryption at rest
- SQS managed encryption
- S3 public access blocked
- DynamoDB point-in-time recovery
- bucket and table retained during stack deletion

## Cost model

The system is intentionally explained through measurable usage:

- S3 stored bytes, versions, and requests
- Lambda invocation count, duration, and memory
- DynamoDB conditional writes, reads, storage, and recovery
- SQS failure traffic and retention
- CloudWatch log ingestion, retention, metrics, and alarms

![Cost drivers](assets/cost-drivers.svg)

The repo does not promise a fixed universal price because AWS cost depends on region, traffic, retention, object sizes, and account usage.

## Project history

- **February 2025:** early S3-to-DynamoDB metadata-table discussions established the technical precursor.
- **May to August 2025:** the design became an AWS internship serverless metadata capstone.
- **July 2025:** the completed system was described as an S3 upload to Lambda extraction to DynamoDB storage workflow with monitoring, security, testing, frontend presentation, and cost reasoning.
- **August 2026:** the public reconstruction added deployable infrastructure, production-style code, tests, CI, failure handling, runbooks, diagrams, and GitHub Pages documentation.

See [Project History](docs/project-history.md).

## Truthful public description

> Built an event-driven AWS metadata workflow during an AWS Support Engineering internship using S3, Lambda, DynamoDB, and a static frontend layer; created a measurable usage-based cost model and later reconstructed the system publicly with AWS SAM, idempotent writes, monitoring, tests, security controls, diagrams, and full technical documentation.

### This repository does not claim

- production customer ownership
- live enterprise ticket ownership
- unrestricted Amazon administrative access
- that every public file is the exact original internal internship file
- that confidential Amazon material is included

## Repository structure

```text
.
├── .github/workflows/validate.yml
├── assets/
│   ├── architecture-overview.svg
│   ├── cost-drivers.svg
│   ├── data-model.svg
│   ├── processing-flow.svg
│   └── security-boundary.svg
├── docs/
│   ├── architecture-decisions/001-event-driven-serverless.md
│   ├── accessibility.md
│   ├── architecture.md
│   ├── cost-model.md
│   ├── data-contract.md
│   ├── deployment.md
│   ├── faq.md
│   ├── implementation-notes.md
│   ├── interview-guide.md
│   ├── operations-runbook.md
│   ├── project-history.md
│   ├── security-and-scope.md
│   ├── testing-and-validation.md
│   └── troubleshooting.md
├── events/
│   ├── README.md
│   └── s3-object-created.json
├── src/metadata_extractor/
│   ├── __init__.py
│   └── app.py
├── tests/test_app.py
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── SECURITY.md
├── index.html
├── pyproject.toml
├── requirements-dev.txt
├── styles.css
└── template.yaml
```

## Documentation index

| Area | Document |
|---|---|
| Architecture | [Architecture](docs/architecture.md) |
| Decision record | [ADR 001](docs/architecture-decisions/001-event-driven-serverless.md) |
| Implementation | [Implementation Notes](docs/implementation-notes.md) |
| Deployment | [Deployment Guide](docs/deployment.md) |
| Data | [Metadata Data Contract](docs/data-contract.md) |
| Operations | [Operations Runbook](docs/operations-runbook.md) |
| Troubleshooting | [Troubleshooting Guide](docs/troubleshooting.md) |
| Security | [Security and Scope](docs/security-and-scope.md) |
| Cost | [Cost Model](docs/cost-model.md) |
| Testing | [Testing and Validation](docs/testing-and-validation.md) |
| Accessibility | [Accessibility Notes](docs/accessibility.md) |
| History | [Project History](docs/project-history.md) |
| Interviews | [Interview Guide](docs/interview-guide.md) |
| FAQ | [Frequently Asked Questions](docs/faq.md) |

## Author

**Bradley Matera**  
Full-Stack Software Engineer  
AWS Certified Solutions Architect - Associate  
AWS Certified AI Practitioner  
U.S. Army veteran

- Portfolio: https://bradleymatera.dev/recruiter/
- LinkedIn: https://www.linkedin.com/in/bradmatera/
- GitHub: https://github.com/BradleyMatera

## License

[MIT](LICENSE)
