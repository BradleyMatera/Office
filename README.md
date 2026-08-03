# AWS Serverless Metadata Workflow

[![Validate Serverless Metadata Workflow](https://github.com/BradleyMatera/Office/actions/workflows/validate.yml/badge.svg)](https://github.com/BradleyMatera/Office/actions/workflows/validate.yml)
[![Monitor GitHub Pages Health](https://github.com/BradleyMatera/Office/actions/workflows/site-health.yml/badge.svg)](https://github.com/BradleyMatera/Office/actions/workflows/site-health.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-1f883d)](https://bradleymatera.github.io/Office/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A deployable, tested, officially sourced, and fully documented public reconstruction of the AWS serverless metadata workflow I built during my AWS Support Engineering internship.

## Public AWS hub

- **Workflow walkthrough:** https://bradleymatera.github.io/Office/
- **AWS writing:** https://bradleymatera.github.io/Office/writing.html
- **Proof map:** https://bradleymatera.github.io/Office/proof.html
- **Verified AWS sources:** https://bradleymatera.github.io/Office/sources.html
- **Design system:** https://bradleymatera.github.io/Office/design-system.html
- **Recruiter portfolio:** https://bradleymatera.dev/recruiter/

![AWS Serverless Metadata Workflow architecture](assets/architecture-overview.svg)

## What the system does

1. A file is uploaded under a configurable Amazon S3 key prefix, defaulting to `incoming/`.
2. S3 sends an object-created notification to AWS Lambda.
3. The Python 3.12 function validates the event, URL-decodes the object key, and calls `HeadObject`.
4. It normalizes current object metadata into a versioned data contract.
5. It creates a deterministic SHA-256 `RecordId` from the bucket, decoded key, version ID, and ETag.
6. It writes the item to DynamoDB with `attribute_not_exists(RecordId)` so repeated event delivery is safe.
7. Unexpected failures are raised for Lambda asynchronous retry.
8. Events that still fail are sent to an encrypted SQS destination.
9. CloudWatch alarms monitor Lambda errors, Lambda throttles, and failed events waiting in the queue.
10. An optional SNS email path makes those alarms actionable after the recipient confirms the subscription.

The implementation reads object headers. It does **not** download or parse the complete file body.

## Why this repository exists

The original work was completed in isolated AWS internship training and project environments without production customer data. This repository preserves the real architecture, engineering decisions, cost reasoning, and troubleshooting process while intentionally excluding confidential or internal-only material.

The repository is both:

- the permanent AWS internship walkthrough linked from my resumes
- a deployable AWS SAM application that an authorized user can validate, test, build, and deploy
- an AWS writing hub that links to canonical articles on my personal site and selected DEV editions
- a transparent proof map separating original implementation evidence from supporting context
- an official-source verification layer mapping service claims to current AWS documentation

## Verified status

An independent local audit on August 3, 2026 produced:

- **11 passing tests**
- **100% statement coverage**
- **100% branch coverage**

The repository CI requires at least 85% coverage and also performs:

- Python compilation
- Ruff linting across `src`, `tests`, and `scripts`
- static-site validation
- AWS SAM template linting
- AWS SAM application build

A separate scheduled workflow checks the live GitHub Pages routes, CSS, social preview, sitemap, RSS feed, and machine-readable project summary.

## Infrastructure implemented

### Amazon S3

- server-side encryption
- versioning
- bucket-owner-enforced object ownership with ACLs disabled
- all four Block Public Access controls
- configurable processing prefix
- incomplete multipart-upload cleanup
- retained-data policy during stack deletion

### AWS Lambda

- Python 3.12 ARM64 runtime
- 256 MB memory and 30-second timeout
- active X-Ray tracing
- least-privilege SAM policy templates
- version-aware `HeadObject` requests
- structured JSON logs
- one-hour maximum asynchronous event age
- two asynchronous retry attempts
- encrypted SQS on-failure destination

### Amazon DynamoDB

- on-demand billing
- encrypted storage
- deterministic `RecordId` partition key
- conditional idempotent writes
- point-in-time recovery
- retained-data policy during stack deletion

### Operations

- encrypted SQS failure queue
- configurable CloudWatch Logs retention, defaulting to 14 days
- Lambda error alarm
- Lambda throttle alarm
- failure-queue depth alarm
- optional SNS topic and confirmed email subscription
- deployment, recovery, troubleshooting, and cleanup runbooks

## Lambda behavior

- validates the S3 event major version
- rejects unsupported event sources and empty record lists
- URL-decodes S3 keys with `unquote_plus`
- sends a version ID to `HeadObject` when present
- normalizes required and optional metadata fields
- stores custom S3 user metadata without logging object contents
- records checksums when S3 supplies them
- creates deterministic SHA-256 identity
- treats a conditional-check failure as a safe duplicate
- aggregates failed record indexes and raises unexpected failures for retry
- lazily creates and reuses AWS SDK clients across warm invocations

## Architecture

```text
Upload under configured prefix
            |
            v
       Amazon S3
            |
       ObjectCreated
            v
       AWS Lambda ---------------> CloudWatch Logs and alarms
            |
        HeadObject
            |
    normalize metadata
            |
 conditional PutItem
            v
    Amazon DynamoDB

Unexpected asynchronous failure
            |
       Lambda retries
            |
            v
 encrypted SQS failure queue ----> queue-depth alarm ----> optional SNS email
```

The public GitHub Pages site is separate from the private AWS deployment. It contains code, documentation, writing previews, examples, and diagrams, but no AWS credentials and no direct access to uploaded objects or cloud resources.

![Security boundary](assets/security-boundary.svg)

## Normalized metadata record

The DynamoDB partition key is `RecordId`, a deterministic SHA-256 hash derived from:

- bucket name
- decoded object key
- object version ID, when present
- ETag

Representative item:

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

See [Metadata Data Contract](docs/data-contract.md).

## Quick start

### Prerequisites

- Python 3.12
- AWS CLI
- AWS SAM CLI
- Docker when a containerized SAM build is required
- authorized AWS credentials

### Run every local check

```bash
make install
make check
```

Individual commands:

```bash
make compile
make lint
make test
make site
make validate
make build
```

### Deploy

```bash
sam deploy --guided \
  --stack-name aws-serverless-metadata-workflow \
  --region us-east-1
```

The guided deployment asks for:

- `InputPrefix`, default `incoming/`
- `LogRetentionDays`, default `14`
- optional `AlarmEmail`

When an email is supplied, the recipient must confirm the SNS subscription before alarm notifications are delivered.

### Read outputs

```bash
make outputs
```

### Trigger the workflow

```bash
printf 'metadata workflow test\n' > sample.txt

aws s3 cp sample.txt \
  s3://YOUR_UPLOAD_BUCKET/incoming/sample.txt \
  --content-type text/plain \
  --metadata source=readme
```

### Verify processing

```bash
aws logs tail /aws/lambda/YOUR_FUNCTION_NAME \
  --region us-east-1 \
  --since 10m \
  --follow

aws dynamodb scan \
  --region us-east-1 \
  --table-name YOUR_METADATA_TABLE \
  --max-items 10
```

Read the [Deployment Guide](docs/deployment.md) before creating or deleting resources.

## Reliability model

### At-least-once event delivery

S3 Event Notifications can be delivered more than once and are not globally ordered. The implementation records the S3 sequencer and uses deterministic identity plus a conditional write rather than assuming exactly-once delivery.

### Idempotency

```text
ConditionExpression = attribute_not_exists(RecordId)
```

A repeated identity returns `duplicate` instead of creating another item.

### Retries and failed events

The SAM template configures:

- maximum event age: 3,600 seconds
- maximum retry attempts: 2
- encrypted SQS on-failure destination
- queue-depth alarm for messages waiting for investigation

The [Operations Runbook](docs/operations-runbook.md) explains controlled investigation and replay.

### Data protection and deletion

The upload bucket and metadata table use `DeletionPolicy: Retain` and `UpdateReplacePolicy: Retain`. Deleting the stack therefore does not silently destroy uploaded files or metadata.

A retained versioned bucket can also retain its event-notification configuration after stack deletion. Before deleting or repurposing the bucket, inspect and intentionally remove or replace that notification configuration so it does not reference a deleted Lambda function.

## Cost model

The architecture is explained through measurable usage rather than a universal price claim:

- S3 stored bytes, object versions, and requests
- Lambda invocations, duration, memory, and retries
- DynamoDB writes, reads, storage, and point-in-time recovery
- SQS failure traffic and message retention
- CloudWatch log ingestion, retention, metrics, and alarms
- SNS notification traffic when configured
- static GitHub Pages delivery

![Cost drivers](assets/cost-drivers.svg)

See [Cost Model](docs/cost-model.md) and [AWS Free Tier: What Actually Costs Money](https://bradleymatera.dev/aws-free-tier-honest-guide/).

## AWS writing

The site links to seven canonical articles sourced from the public MDX frontmatter in my blog repository:

- [AWS Cloud Support Internship: What I Actually Practiced](https://bradleymatera.dev/aws-cloud-support-internship-mastering-troubleshooting-and-architecture/)
- [How I Built ProjectHub: An Embeddable AI Recruiter Assistant That Runs on Free Tiers](https://bradleymatera.dev/projecthub-embeddable-ai-recruiter-free-tiers/)
- [AWS Free Tier: What Actually Costs Money](https://bradleymatera.dev/aws-free-tier-honest-guide/)
- [AWS vs. Azure vs. Google Cloud: A 2026 Free Tier Comparison From Real Use](https://bradleymatera.dev/aws-vs-azure-vs-google-cloud/)
- [Cognito Authentication With React: A Small, Verifiable Setup](https://bradleymatera.dev/secure-authentication-cognito-react/)
- [Certifications and Continuous Learning: A Simple Track](https://bradleymatera.dev/certifications-continuous-learning/)
- [From Combat Medic to Software Engineer: Translating a Non-Traditional Background](https://bradleymatera.dev/from-medic-to-engineer/)

The [AWS Writing Hub](writing.html) provides teasers and selected DEV editions without copying full articles into this repository.

## Proof and official-source verification

- [Proof Map](proof.html) identifies what each repository, credential, article source, and test result establishes and what it does not prove.
- [Verified AWS Sources](sources.html) maps load-bearing claims to current official AWS documentation.
- [Verified AWS Sources, Markdown](docs/verified-aws-sources.md) preserves the same mapping in the repository.
- [AWS Evidence Design System](design-system.html) documents the visible visual and content contract.
- [Design System Specification](docs/design-system.md) defines tokens, components, accessibility, SEO, illustration rules, and content governance.

## Production web surface

The GitHub Pages project includes:

- workflow landing page
- AWS writing hub
- proof map
- official AWS source map
- visible design-system reference
- custom 404 recovery page
- first-party architecture and editorial SVG assets
- 1200×630 social preview PNG
- Open Graph and Twitter metadata
- JSON-LD for software, site, collection, profile, technical article, and FAQ content
- `robots.txt`
- `sitemap.xml`
- `rss.xml`
- `llms.txt`
- `humans.txt`
- `site.webmanifest`
- static validation and daily live-site health monitoring

## Project history

- **February 2025:** early S3-to-DynamoDB metadata-table discussions established the technical precursor.
- **May to August 2025:** the design became an AWS internship serverless metadata capstone.
- **July 2025:** the completed system was described as S3 upload to Lambda metadata extraction to DynamoDB storage, with monitoring, security, testing, frontend presentation, and cost reasoning.
- **August 2026:** the public reconstruction added deployable infrastructure, production-style code, tests, CI, failure handling, alarms, runbooks, original graphics, AWS writing, proof, official-source verification, a design system, SEO files, and live Pages monitoring.

See [Project History](docs/project-history.md).

## Truthful public description

> Built an event-driven AWS metadata workflow during an AWS Support Engineering internship using S3, Lambda, DynamoDB, and a static frontend layer; created a measurable usage-based cost model and later reconstructed the system publicly with AWS SAM, idempotent writes, retries, an encrypted failure queue, actionable monitoring, tests, security controls, original diagrams, verified official AWS sources, and full technical documentation.

### This repository does not claim

- production customer ownership
- live enterprise ticket ownership
- unrestricted Amazon administrative access
- that every public file is the exact original internal internship file
- that confidential Amazon material is included
- that a live AWS stack is currently connected to the GitHub Pages site

## Repository structure

```text
.
├── .github/workflows/
│   ├── site-health.yml
│   └── validate.yml
├── assets/
│   ├── content/
│   ├── og/aws-metadata-workflow.png
│   ├── architecture-overview.svg
│   ├── cost-drivers.svg
│   ├── data-model.svg
│   ├── processing-flow.svg
│   └── security-boundary.svg
├── data/aws-content.json
├── docs/
│   ├── architecture-decisions/001-event-driven-serverless.md
│   ├── accessibility.md
│   ├── architecture.md
│   ├── cost-model.md
│   ├── data-contract.md
│   ├── deployment.md
│   ├── design-system.md
│   ├── faq.md
│   ├── implementation-notes.md
│   ├── interview-guide.md
│   ├── operations-runbook.md
│   ├── project-history.md
│   ├── security-and-scope.md
│   ├── testing-and-validation.md
│   ├── troubleshooting.md
│   └── verified-aws-sources.md
├── events/
│   ├── README.md
│   └── s3-object-created.json
├── scripts/validate_site.py
├── src/metadata_extractor/
│   ├── __init__.py
│   └── app.py
├── tests/test_app.py
├── 404.html
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── SECURITY.md
├── design-system.html
├── favicon.svg
├── hub.css
├── humans.txt
├── index.html
├── llms.txt
├── proof.html
├── pyproject.toml
├── requirements-dev.txt
├── robots.txt
├── rss.xml
├── site.webmanifest
├── sitemap.xml
├── sources.html
├── styles.css
├── template.yaml
└── writing.html
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
| Verified AWS behavior | [Verified AWS Sources](docs/verified-aws-sources.md) |
| Design system | [AWS Evidence Design System](docs/design-system.md) |
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
