# Troubleshooting Guide

## GitHub Pages shows a 404

Check:

- repository visibility is public
- Pages source is the `main` branch and `/(root)`
- `index.html` exists in the repository root
- the published URL matches the repository name exactly

A repository rename changes the project Pages URL.

## Diagrams do not load

The site uses relative paths such as `assets/architecture-overview.svg`. Confirm the files exist with the same capitalization. GitHub Pages paths are case-sensitive.

## `sam validate --lint` fails

- confirm the AWS SAM CLI is installed
- run the command from the repository root
- confirm `template.yaml` is valid YAML
- inspect the exact resource and property named in the validation output

Do not remove encryption, public-access blocks, retention controls, or IAM boundaries merely to make validation pass.

## `sam build` cannot resolve Python

The function runtime is Python 3.12. Install Python 3.12 or use a containerized SAM build:

```bash
sam build --use-container
```

## Deployment reports an S3 bucket naming error

The template does not force a bucket name. CloudFormation creates a globally unique physical name. Avoid adding a fixed name unless you have a clear naming and collision strategy.

## Upload succeeds but no DynamoDB record appears

1. confirm the object exists
2. inspect the Lambda error metric and logs
3. confirm the S3 notification exists on the deployed bucket
4. confirm `TABLE_NAME` matches the stack output
5. check the failure queue
6. verify the function role can call `s3:HeadObject` and write to the table

## Object key looks wrong

S3 notification keys are URL-encoded. The Lambda handler uses `unquote_plus`, so an event key such as:

```text
incoming%2Fquarterly+report.pdf
```

becomes:

```text
incoming/quarterly report.pdf
```

## The same event appears twice

Asynchronous systems can deliver events more than once. The function creates a deterministic `RecordId` and uses a conditional DynamoDB write. A repeated identity is logged as `duplicate` rather than creating another item.

## A replacement upload creates another record

The bucket has versioning enabled. A new object version has a different version ID and is intentionally recorded as a separate metadata item.

## The failure queue contains messages

Do not immediately delete them. Use the operations runbook:

1. identify the underlying exception
2. correct permissions, configuration, or data issues
3. confirm whether an item already exists
4. replay safely
5. verify the recovered record
6. delete only after recovery

## Stack deletion leaves resources behind

This is intentional. The upload bucket and metadata table use retention policies to avoid accidental data loss. Review and remove retained resources manually when appropriate.
