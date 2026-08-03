# Contributing

This repository contains a deployable AWS demonstration and the public documentation for an internship capstone. Corrections and focused improvements are welcome when they preserve the documented scope, security boundaries, accessibility requirements, and validation workflow.

## Before contributing

- keep claims consistent with the documented internship scope
- do not add confidential Amazon material or internal-only details
- do not commit AWS credentials, account IDs, private bucket names, object contents, or sensitive logs
- keep the architecture deployable through AWS SAM
- preserve idempotent event handling
- use official AWS documentation for important service-behavior claims
- use canonical MDX frontmatter for personal article dates, titles, and slugs
- do not present forks, design plans, or resume files as deployed engineering proof
- explain the project directly instead of adding meta copy about how recruiters should read it

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

Do not submit a change after running only the check that covers the edited file. The site, documentation, code, and infrastructure cross-reference one another.

## Lambda changes

- add or update focused unit tests
- preserve deterministic identity and idempotent behavior unless an intentional design change is documented
- preserve unexpected-error propagation for Lambda retry
- do not download full object contents unless a documented requirement and cost model are added
- keep structured logs free of object contents and secrets
- document new metadata fields in `docs/data-contract.md`
- increment `SchemaVersion` for compatibility-breaking data changes

## Infrastructure changes

- update `template.yaml`
- document new resources and cost drivers
- review least-privilege permissions
- explain alarm, retry, failure, cleanup, and data-retention behavior
- update deployment, operations, and troubleshooting documentation
- update `docs/verified-aws-sources.md` when an important AWS assumption changes
- preserve the distinction between template validation and a verified real deployment

## Public-page changes

- preserve one visible `h1` and one `main` landmark per page
- preserve the skip link
- use a unique title, description, canonical URL, and structured-data type
- add meaningful `alt` text for images
- add `<title>` and `<desc>` to first-party SVGs
- update the sitemap when a public page is added or removed
- update the live-health workflow when a critical route or page identity changes
- update `llms.txt` when the public project description changes materially
- run `python scripts/validate_site.py`

### Interface rules

The public pages follow the visual foundation and information patterns of Cloudscape using semantic HTML and CSS.

- make shared changes in `styles.css` or `hub.css`
- follow the tokens and component rules in `docs/design-system.md`
- do not create a separate public page to explain the design system
- do not add one-off marketing gradients, giant display headings, decorative glass panels, or animation that competes with the project explanation
- use normal technical headings such as Overview, Architecture, Reliability, Evidence, and Project scope
- do not add sections such as “what recruiters will see,” “how to use this page,” or “five-minute recruiter path”
- preserve reduced-motion support, keyboard focus, semantic landmarks, and responsive reflow
- keep the interface clearly independent from AWS and do not imply AWS endorsement

## Article changes

- use the personal blog as canonical when the article exists there
- use DEV as a secondary distribution link
- source dates and slugs from the public blog repository frontmatter
- add article metadata to `data/aws-content.json`
- do not present a future publication date as already published
- add a relevant first-party illustration and descriptive alternative text
- keep teasers short enough that the full article remains worth visiting

## Documentation changes

- distinguish verified project history from future improvements
- prefer specific, plain wording
- expand service names before relying on abbreviations
- keep links and commands current
- keep positive evidence and claim boundaries visible near the claims they qualify
- do not replace official AWS links with secondary tutorials

## Binary and generated assets

- use first-party assets with clear ownership
- optimize dimensions for their intended use
- preserve editable source where practical
- use a 1200×630 PNG for the primary social preview
- never commit fonts, credentials, private-account screenshots, or unlicensed stock imagery

## Validation expectations

| Change | Minimum evidence |
|---|---|
| Lambda behavior | unit test, coverage, lint, explanation |
| SAM resource | SAM lint, SAM build, documentation and cost update |
| Public page | static validator, responsive and keyboard review |
| Article teaser | canonical source check, content-index update, asset check |
| AWS behavior claim | current primary AWS documentation |
| Interface token or component | rendered page review and accessibility check |
| Alarm or failure path | runbook and deployment update |

## Pull requests

Direct updates to `main` are used for the owner's rapid content workflow. External contributors should use a branch and pull request.

A pull request should explain:

- what changed
- why it changed
- how it was tested
- whether security, cost, retention, cleanup, or public claims changed
- whether canonical URLs, sitemap entries, or health checks changed

Do not call a change production-ready solely because the local build passed. State which layers were verified:

- local unit behavior
- static site
- SAM template and build
- live GitHub Pages
- deployed AWS integration
