# AWS Serverless Metadata Workflow - Resume Reference

Last verified: August 3, 2026

Use this file as the wording and link source of truth whenever this project appears on a resume, cover letter, application profile, recruiter page, LinkedIn entry, or interview-preparation document.

## Canonical Project Name

**AWS Serverless Metadata Workflow**

Do not shorten the formal project name to `Metadata Extractor`, `AWS Metadata Project`, `Lambda Project`, or `Office` in resume-facing materials.

## Canonical Links

- Resume-facing walkthrough: https://bradleymatera.dev/aws-metadata-workflow/
- GitHub Pages deployment: https://bradleymatera.github.io/Office/
- Source repository: https://github.com/BradleyMatera/Office
- Internship article: https://bradleymatera.dev/aws-cloud-support-internship-mastering-troubleshooting-and-architecture/

Use the resume-facing walkthrough as the first link on resumes. Use the source repository as the second link when space permits.

## One-Line Resume Version

Built an AWS internship capstone in an isolated training environment using S3, Lambda, DynamoDB, and an accessible frontend; later reconstructed it publicly with AWS SAM, idempotent writes, failure handling, tests, CI, diagrams, and a usage-based cost model.

## Shorter Resume Version

Built an event-driven S3-to-Lambda-to-DynamoDB metadata workflow during an AWS internship and later reconstructed it publicly with AWS SAM, tests, CI, failure handling, and technical documentation.

## Cloud-Focused Resume Version

Built an event-driven AWS metadata workflow using S3, Lambda, and DynamoDB in an isolated internship environment; reconstructed it publicly with AWS SAM and CloudFormation, deterministic record identity, conditional writes, retry controls, an SQS failure destination, CloudWatch alarms, tests, CI, and operating runbooks.

## Support-Focused Resume Version

Built and troubleshot an AWS serverless metadata workflow involving S3 events, Lambda processing, DynamoDB persistence, permissions, logs, failure investigation, documentation, and measurable usage-based cost inputs in an isolated internship environment.

## Data-Focused Resume Version

Designed an S3-to-Lambda-to-DynamoDB workflow that normalizes uploaded-object metadata into structured records, then reconstructed the system publicly with a documented data contract, deterministic record identity, idempotent writes, tests, and CI.

## Thirty-Second Interview Explanation

The original project was my AWS internship capstone. A file upload to S3 triggered Lambda, the function extracted and normalized the object metadata, and DynamoDB stored the resulting record. I also built the presentation layer and a usage-based cost model. The original work was completed in isolated training and project environments, not in a production customer account. I later rebuilt the architecture publicly with AWS SAM, Python tests, idempotent writes, retries, an SQS failure path, CloudWatch alarms, diagrams, and operating documentation so employers can inspect the work without exposing internal Amazon material.

## What the Original Project Proves

- Foundational AWS service integration
- Event-driven architecture understanding
- S3 event, Lambda, and DynamoDB workflow construction
- Permissions, logs, configuration, and failure-investigation practice
- Accessible technical presentation
- Cloud cost-awareness using measurable usage inputs
- Ability to explain the system and its boundaries clearly

## What the Public Reconstruction Proves

- AWS SAM and CloudFormation infrastructure design
- Python 3.12 Lambda implementation
- URL-decoded and version-aware S3 object handling
- Deterministic metadata-record identity
- Idempotent DynamoDB conditional writes
- Asynchronous retry and failure-destination configuration
- Encrypted S3, DynamoDB, and SQS resources
- CloudWatch monitoring and alarms
- Unit tests, coverage, linting, CI, diagrams, and runbooks

## Current Verification Record

- 11 Python unit tests passed during the August 3, 2026 audit.
- The audited implementation reported 100% statement and branch coverage.
- Role-specific resume PDFs containing the linked project entry remained one page in the Cloud Support Engineer, Data Engineer, and Changeis Junior Cloud Engineer samples checked after regeneration.
- The PDFs contain clickable annotations for the clean walkthrough and GitHub repository links.

## Required Scope Boundary

Always say that the original project was completed in isolated internship training and project environments.

Never claim:

- production customer data
- production customer-system ownership
- live enterprise ticket ownership
- an enterprise on-call rotation
- unrestricted Amazon administrative access
- measured company cost savings
- that the public repository is an exact dump of internal Amazon files
- that the public AWS stack was deployed from this environment when it was not

## Verified Architecture Behavior

The public implementation intentionally reflects current AWS-documented behavior:

- Amazon S3 Event Notifications are delivered at least once and can be duplicated or arrive out of order.
- S3 `HeadObject` retrieves object metadata without returning the object body.
- Lambda asynchronous invocation settings can limit event age and retry attempts and can send failed invocation records to an SQS destination.
- DynamoDB conditional `PutItem` with `attribute_not_exists(RecordId)` prevents an existing record with the same primary key from being overwritten.

Official documentation links are maintained on the site's Verified AWS Sources appendix.

## Resume Placement Rules

Use this project prominently for:

- Cloud Support Engineer
- Junior Cloud Engineer
- Cloud Operations
- DevOps or infrastructure support
- Data Engineer or data automation
- Systems Support Engineer
- Technical Support roles with cloud responsibilities
- Application Support roles involving integrations, logs, or incident handling

Do not force it into resumes where cloud, technical systems, data flow, support, or architecture are not relevant.
