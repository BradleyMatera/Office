# Frequently Asked Questions

## Did this run against production customer data?

No. The internship work was completed in isolated training and project environments. This public repository does not claim production customer ownership or access.

## Is this the exact internal Amazon repository?

No. This is a public reconstruction and technical case study based on the architecture and work Bradley Matera completed during the internship. Confidential or internal-only material is intentionally excluded.

## What metadata does the function extract?

The deployable version records object-level information available from the S3 event and `HeadObject`, including the bucket, decoded object key, file name, size, content type, ETag, timestamps, storage class, version ID, checksum fields when present, and custom user metadata.

## Does the function read the entire file?

No. The current implementation reads object headers through `HeadObject`. It does not download or parse the full file body.

## Why use DynamoDB?

The workflow stores lightweight keyed metadata records and does not currently require relational joins. DynamoDB provides a low-operations persistence layer that fits the event-driven design.

## Why use on-demand billing?

The demonstration workload is unpredictable and may remain idle for long periods. On-demand mode avoids managing provisioned read and write capacity for that pattern.

## What happens if S3 delivers the event more than once?

The function calculates a deterministic record ID and uses a conditional DynamoDB write. A repeated identity is treated as a successful duplicate rather than creating another item.

## What happens after repeated failures?

Lambda retries the asynchronous invocation according to the template settings. An event that still fails is sent to an encrypted SQS failure queue for controlled investigation and replay.

## Why are the S3 bucket and DynamoDB table retained during stack deletion?

The retention policy reduces the chance of destroying uploaded files or metadata accidentally. Removing retained data is a separate intentional cleanup decision.

## Does the site expose a live AWS account?

No. GitHub Pages hosts the public documentation. It does not expose AWS credentials or provide direct access to a deployed bucket or table.

## Can somebody deploy the code themselves?

Yes, using an AWS account they are authorized to manage, the AWS CLI, and AWS SAM CLI. The deployment guide explains the process and responsibilities.

## What did Bradley personally do?

The documented core is the serverless metadata workflow built during the AWS Support Engineering internship, including the Lambda, DynamoDB, S3, static presentation layer, cost reasoning, and technical explanation. The public repository expands that work into a deployable, tested, recruiter-safe case study.

## Why is the repository still named `Office`?

The project was initially built inside an existing empty public repository because the connected GitHub tooling could edit repositories but could not create or rename the repository shell. The repository can be renamed without changing the project contents; the GitHub Pages URL will change to match the new name.
