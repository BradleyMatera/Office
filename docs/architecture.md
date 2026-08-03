# Architecture

## Overview

The AWS Serverless Metadata Workflow uses a simple event-driven architecture built around four primary responsibilities:

1. **Storage** — accept uploaded files
2. **Triggering** — react automatically to object creation
3. **Processing** — extract and normalize metadata
4. **Persistence and presentation** — store metadata and communicate the system clearly

## Primary Services

### Amazon S3

Amazon S3 acts as the intake layer. Uploaded files are stored in a bucket that serves as the event source for the workflow.

### AWS Lambda

A Lambda function performs the extraction logic. This keeps the processing layer serverless and event-driven rather than requiring manually managed compute infrastructure.

### Amazon DynamoDB

DynamoDB stores normalized metadata records. The public documentation refers to the table as `FileMetadata` to illustrate the purpose of the persistence layer without relying on internal-only naming details.

### Static Frontend Layer

A static frontend provides a public-safe explanation of the workflow, architecture, and cost model. In the project context, the delivery layer can reasonably be represented as S3 + CloudFront or Amplify for static hosting and fast delivery.

## Why this architecture works well

- **Serverless**: no always-on servers to patch or manage
- **Event-driven**: the system only runs when work exists
- **Composable**: each service has a narrow responsibility
- **Cost-aware**: usage can be reasoned about by request counts, storage, execution duration, and reads/writes
- **Demonstrable**: the workflow can be explained clearly to technical and non-technical audiences

## Public-safe boundaries

This documentation intentionally stays at the architecture and engineering-principles level. It does not disclose internal-only source code, sensitive account information, or anything involving production customer data.

## Diagram

![Architecture overview](../assets/architecture-overview.svg)
