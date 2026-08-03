# Project History

## February 2025: technical precursor

The earliest recovered discussion connected Amazon S3 object information with a DynamoDB metadata table. The early design questions included:

- what to name the table
- which value should be the partition key
- whether a sort key was useful
- how S3 file metadata should be written into DynamoDB
- whether the process should be automated with Lambda or command-line tooling

This was the recognizable technical foundation of the later workflow, although it was not yet the completed AWS internship capstone.

## May through August 2025: AWS Support Engineering internship

During the AWS internship, the project developed into a serverless metadata workflow using:

- Amazon S3 as the file intake and event source
- AWS Lambda as the event-driven metadata processor
- Amazon DynamoDB as the metadata persistence layer
- a static frontend delivery layer using AWS services such as CloudFront or Amplify
- measurable cloud-usage inputs for cost reasoning

The work was completed in isolated training and project environments without production customer data.

## July 2025: completed capstone discussion

By July 2025, the project was being described as a serverless event-driven metadata extraction system with a flow equivalent to:

```text
S3 upload -> Lambda metadata extraction -> DynamoDB storage
```

The completed discussion also included monitoring, IAM and security, testing, cost analysis, and the static frontend presentation layer.

## August 2026: public reconstruction

This repository turns the original capstone into a complete public portfolio artifact by adding:

- a deployable AWS SAM template
- a production-style Python Lambda implementation
- idempotent DynamoDB writes
- encryption, retries, a failure queue, logging retention, and an error alarm
- unit tests, linting, coverage, SAM validation, and CI builds
- architecture, processing, security, data-model, and cost graphics
- deployment, operations, troubleshooting, accessibility, and data-contract documentation
- a GitHub Pages case-study site

## Important distinction

The public repository is a faithful engineering reconstruction and expansion of the original project. It is not a claim that every public file is the exact internal file used during the internship. Confidential or internal-only details are intentionally excluded.
