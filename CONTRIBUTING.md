# Contributing

This repository is primarily a public technical case study and deployable AWS demonstration. Corrections and focused improvements are welcome when they preserve the documented internship scope, security boundaries, accessibility contract, and production validation workflow.

## Before contributing

- keep all claims consistent with the documented internship scope
- do not add confidential Amazon material or internal-only details
- do not commit AWS credentials, account IDs, private bucket names, object contents, or sensitive logs
- keep the architecture deployable through AWS SAM
- preserve idempotent event handling
- preserve accessibility and plain-language documentation
- use official AWS documentation for load-bearing service claims
- use canonical MDX frontmatter for personal article dates, titles, and slugs
- do not present forks or design plans as original deployed proof

## Run the complete local check

```bash
make install
make check
```

`make check` performs:

1. Python compilation
2. Ruff linting
3. unit tests and branch coverage
4. static-site validation
5. AWS SAM linting
6. AWS SAM build

Individual commands:

```bash
make compile
make lint
make test
make site
make validate
make build
```

Do not submit a change after running only the check that covers the file you edited. The site, docs, code, and infrastructure cross-reference one another.

## Change expectations

### Lambda changes

- add or update focused unit tests
- preserve deterministic identity and idempotent behavior unless an intentional design change is documented
- preserve unexpected-error propagation for Lambda retry
- do not download full object contents unless a documented requirement and cost model are added
- keep structured logs free of object contents and secrets
- document new metadata fields in `docs/data-contract.md`
- increment `SchemaVersion` when a compatibility-breaking data change is introduced

### Infrastructure changes

- update `template.yaml`
- document new resources and cost drivers
- review least-privilege permissions
- explain alarm, retry, failure, cleanup, and data-retention behavior
- update `docs/deployment.md`
- update `docs/operations-runbook.md`
- update `docs/troubleshooting.md`
- update `docs/verified-aws-sources.md` when a load-bearing AWS assumption changes
- preserve the distinction between template validation and a verified real deployment

### Public-page changes

- preserve one visible `h1` and one main landmark per page
- preserve the skip link
- use a unique title, description, canonical URL, and structured-data type
- add meaningful `alt` text for images
- add `<title>` and `<desc>` to first-party SVGs
- update the sitemap when a public page is added or removed
- update the live health workflow when a critical route changes
- update `llms.txt` when the public project summary changes materially
- run `python scripts/validate_site.py`

### Article and teaser changes

- use the personal blog as canonical when the article exists there
- use DEV as a secondary distribution link rather than a canonical replacement
- source dates and slugs from the public blog repository frontmatter
- add article metadata to `data/aws-content.json`
- do not add a future publication date as already published
- add a relevant first-party illustration and descriptive alternative text
- keep teasers short enough that the full article remains worth visiting

### Design-system changes

- update `styles.css` or `hub.css` through shared tokens and component contracts
- avoid one-off visual rules when an existing component can be extended
- update `docs/design-system.md` for material token or component changes
- update `design-system.html` when a new public component pattern is introduced
- preserve reduced-motion and forced-colors behavior
- do not add external font dependencies without a documented performance and accessibility reason

### Documentation changes

- distinguish verified project history from proposed future improvements
- prefer specific, plain wording
- expand service names before relying on abbreviations
- keep links and commands current
- keep positive evidence and claim boundaries equally visible
- do not replace official AWS source links with secondary tutorials

### Generated or binary assets

- use first-party assets with clear ownership
- optimize dimensions for their intended use
- preserve editable source where practical
- use a 1200×630 PNG for the primary social preview
- never commit fonts, credentials, screenshots containing private account data, or unlicensed stock imagery

## Validation expectations by change type

| Change | Minimum evidence |
|---|---|
| Lambda behavior | unit test, coverage, lint, explanation |
| SAM resource | SAM lint, SAM build, docs and cost update |
| Public page | static validator, responsive and keyboard review |
| Article teaser | canonical source check, content-index update, local asset check |
| Official-source claim | current primary AWS documentation |
| Design token | rendered design-system update and accessibility review |
| Alarm or failure path | runbook and deployment update |

## Pull requests

Direct updates to `main` are used for the owner's rapid content workflow. External contributors should still use a branch and pull request.

A good pull request explains:

- what changed
- why it changed
- how it was tested
- whether security changed
- whether cost changed
- whether data retention or cleanup changed
- whether public claims changed
- whether canonical URLs, sitemap entries, or health checks changed

Do not mark a change “production ready” solely because the local build passed. State which layers were verified:

- local unit behavior
- static site
- SAM template and build
- live GitHub Pages
- deployed AWS integration
