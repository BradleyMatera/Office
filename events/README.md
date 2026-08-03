# Sample Events

`events/s3-object-created.json` is a public-safe example of the notification shape the Lambda function receives when Amazon S3 reports a new object.

The example is useful for:

- understanding the event contract
- unit and integration test planning
- generating local invocation payloads
- explaining URL-encoded S3 object keys

## Generate a fresh AWS SAM event

```bash
sam local generate-event s3 put > events/generated-s3-put.json
```

AWS SAM can generate sample service events for local testing. The generated payload still needs values that match an object available to the environment where the function runs.

## Local invocation limitation

The function calls `HeadObject` and writes to DynamoDB. A raw local invocation therefore needs either:

- access to deployed AWS resources,
- local service emulation such as LocalStack, or
- mocked clients, as used in the unit tests.

For normal development, run `make test` first. Use the deployed integration test only when AWS credentials and a test stack are intentionally available.
