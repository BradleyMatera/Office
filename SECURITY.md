# Security Policy

## Supported version

The `main` branch is the supported public version of this portfolio project.

## Reporting a vulnerability

Do not post credentials, private bucket names, account IDs, object contents, access tokens, or sensitive logs in a public issue.

For a security concern involving this repository:

1. describe the affected file and behavior without including secrets
2. explain the potential impact
3. include safe reproduction steps
4. contact Bradley Matera through the contact information on the recruiter portfolio if private discussion is required

Recruiter portfolio: https://bradleymatera.dev/recruiter/

## Deployment responsibilities

Anyone deploying this project is responsible for:

- using an AWS account they are authorized to manage
- reviewing the CloudFormation change set
- protecting AWS credentials
- using least-privilege access
- controlling who can upload files
- avoiding sensitive data in S3 user metadata
- monitoring costs and operational alerts
- deleting retained resources intentionally when they are no longer needed

## Project boundaries

This repository is a public reconstruction and case study of an internship capstone. It does not include confidential Amazon information, production customer data, or internal credentials.
