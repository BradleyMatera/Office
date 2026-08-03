# Implementation Notes

## Purpose of the workflow

The workflow was built to automate metadata handling for uploaded files using AWS serverless services. The key design objective was to turn a file upload into a structured metadata record without introducing unnecessary operational complexity.

## Core implementation logic

At a high level, the workflow behaves like this:

1. A file is uploaded to S3.
2. S3 emits an object-created event.
3. Lambda is invoked.
4. Lambda reads the relevant object details and extracts metadata.
5. The function shapes those values into a normalized item.
6. The item is persisted into DynamoDB.

## Why Lambda was a good fit

Lambda fits the problem well because the work is discrete and triggered by events. There is no need to keep a server running while the system waits for uploads.

## Why DynamoDB was a good fit

DynamoDB is appropriate when the goal is to persist lightweight, structured records with predictable access patterns and low operational burden.

## Frontend and presentation layer

The original project also included a frontend presentation component. In this public documentation, that layer is represented as a static site because it communicates the workflow cleanly and keeps the public artifact easy to share.

## Cost-awareness as part of implementation

A meaningful part of this project was understanding what drives cost:

- object storage volume
- request counts
- Lambda executions and duration
- database reads and writes
- content delivery and data transfer

That cost-awareness is part of the implementation story, not just a side note.

## Why this public repo exists

This repository translates the project into a recruiter-safe portfolio artifact. It preserves the real technical story while avoiding overclaiming, leaking internal details, or implying production ownership that did not exist.
