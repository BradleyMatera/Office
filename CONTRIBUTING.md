# Contributing

This repository is primarily a public technical case study, but corrections and focused improvements are welcome.

## Before contributing

- keep all claims consistent with the documented internship scope
- do not add confidential Amazon material or internal-only details
- do not commit AWS credentials, account IDs, private bucket names, or sensitive logs
- keep the architecture deployable through AWS SAM
- preserve accessibility and plain-language documentation

## Development checks

```bash
make install
make lint
make test
make validate
make build
```

## Change expectations

### Lambda changes

- add or update unit tests
- preserve idempotent behavior
- do not download full object contents unless a documented requirement is added
- keep structured logs free of object contents and secrets

### Infrastructure changes

- update `template.yaml`
- document new resources and cost drivers
- review least-privilege permissions
- explain cleanup and data-retention behavior

### Documentation changes

- distinguish verified project history from proposed future improvements
- prefer specific, plain wording
- include meaningful alternative text for diagrams
- keep links and deployment commands current

## Pull requests

A good pull request explains:

- what changed
- why it changed
- how it was tested
- whether security, cost, data retention, or public claims changed
