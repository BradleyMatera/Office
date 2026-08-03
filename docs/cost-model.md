# Cost Model

## Why cost modeling mattered

This project was not just about making the workflow run. It was also about understanding what drives cloud usage and how to explain that clearly.

## Major cost drivers

### Amazon S3

S3 cost is influenced by:

- total stored data volume
- storage class used
- request activity such as PUT, GET, and LIST operations

### AWS Lambda

Lambda cost is influenced by:

- number of invocations
- execution duration
- memory configuration

### Amazon DynamoDB

DynamoDB cost is influenced by:

- read operations
- write operations
- storage consumed by items

### Static delivery layer

The static site or frontend layer is influenced by:

- storage of site assets
- content delivery requests
- transfer volume to viewers

## Why this matters in interviews

A lot of portfolio projects stop at “it works.” This one is stronger because it also answers:

- What makes it cost more?
- What scales cheaply?
- Which architectural choices are cost-sensitive?
- How would usage patterns affect operations?

## Example framing

A simple public-safe explanation is:

> The workflow uses measurable usage inputs such as file storage, request activity, Lambda execution, and database reads and writes to estimate cloud cost drivers instead of treating cost as an afterthought.

## Cost-aware engineering mindset

The biggest lesson is that architecture choices are not isolated from operations. Cost-awareness is part of cloud engineering, not a separate discipline.
