# Troubleshooting Guide

## Start with the failing layer

This repository has three separate operating layers:

1. **local and CI validation** — Python, tests, site validation, SAM lint, and SAM build
2. **GitHub Pages** — public static files and resume-facing routes
3. **deployed AWS stack** — S3, Lambda, DynamoDB, SQS, CloudWatch, and optional SNS

A failure in one layer does not automatically mean the other two are broken.

## Local and CI troubleshooting

### `make check` stops at Python compilation

Run:

```bash
python -m compileall src tests scripts
```

Fix the first syntax error reported. The aggregate check intentionally stops before linting or tests when Python cannot compile.

### Ruff fails

Run:

```bash
ruff check src tests scripts
```

Use Ruff's exact rule and line number. Do not disable an entire rule family to avoid fixing one clear issue.

The project targets Python 3.12, so upgrade rules may prefer current language features such as `datetime.UTC`.

### Unit tests fail before collection

Confirm:

- Python 3.12 is active
- development dependencies are installed
- the command runs from the repository root
- `AWS_DEFAULT_REGION`, `AWS_EC2_METADATA_DISABLED`, and `TABLE_NAME` are set by `make test` or the workflow

Install again:

```bash
make install
```

### Coverage falls below 85%

A behavior change likely added an untested path.

Run:

```bash
make test
```

Use the missing-line report to add a focused test. Do not lower the threshold merely to merge a change.

### Static-site validation fails

Run:

```bash
python scripts/validate_site.py
```

The validator reports the page and contract violation. Common findings include:

- missing local asset
- duplicate element ID
- missing image `alt`
- invalid JSON-LD
- bad canonical URL
- missing Open Graph image
- future-dated article metadata
- malformed sitemap or RSS XML
- local fragment with no matching ID
- SVG missing `<title>` or `<desc>`

Fix the source file. Do not remove the validation check unless the production contract is intentionally changed and documented.

### `sam validate --lint` fails

Check:

- AWS SAM CLI is installed
- the command runs from the repository root
- `template.yaml` is valid YAML
- the property is supported for the declared resource type
- conditional lists and intrinsic functions have the expected shape

Do not remove encryption, public-access blocking, ownership controls, retention, alarms, or IAM boundaries merely to make validation pass.

### `sam build` cannot resolve Python

The function runtime is Python 3.12.

Install Python 3.12 or use:

```bash
sam build --use-container
```

### GitHub Actions badge shows unknown or no status

Possible causes:

- the workflow has not run on the current commit yet
- Actions are disabled for the repository
- the badge is cached
- the current connected API does not expose check-run state

Open the repository's **Actions** tab and inspect:

- `Validate Serverless Metadata Workflow`
- `Monitor GitHub Pages Health`

Do not claim a green workflow based only on the presence of a badge.

## GitHub Pages troubleshooting

### Main site shows a 404

Check:

- repository visibility is public
- Pages source is `main` and `/(root)`
- `.nojekyll` exists
- `index.html` exists in the repository root
- the URL uses the repository name exactly

Current URL:

```text
https://bradleymatera.github.io/Office/
```

Renaming the repository changes every Pages URL and requires updating:

- canonical links
- Open Graph URLs
- JSON-LD URLs
- sitemap
- robots sitemap declaration
- RSS self link
- `llms.txt`
- health workflow base URL
- README badges and links
- static-validator `BASE_URL`

### A subpage returns 404

Critical routes are:

- `writing.html`
- `proof.html`
- `sources.html`
- `design-system.html`

Confirm the exact file exists on `main`. GitHub Pages paths are case-sensitive.

### Old content is still visible

Possible causes:

- Pages has not published the latest commit yet
- browser or CDN cache
- the wrong branch or folder is configured
- a stale link points to another repository name

Check the latest commit on `main`, then use a private browser window or a cache-busting query string for diagnosis.

Do not repeatedly rewrite files solely to force a deployment unless the Pages source is confirmed correct.

### CSS is missing

Confirm both files load:

- `styles.css`
- `hub.css`

The public pages use relative paths. A repository rename does not break those relative references, but moving a page into another directory can.

### Diagrams or article artwork do not load

Confirm:

- capitalization matches
- the asset exists under `assets/` or `assets/content/`
- the HTML uses a relative path
- the SVG is valid XML
- the filename has not been changed only in the content index

Run the site validator before publishing.

### Social preview is missing or stale

The expected image is:

```text
assets/og/aws-metadata-workflow.png
```

Confirm:

- the PNG exists
- the public URL returns `Content-Type: image/png`
- Open Graph and Twitter tags use the absolute Pages URL
- the platform's link-preview cache has been refreshed

Social platforms may cache an old preview even after the site is correct.

### Search engines show the wrong date

The canonical article dates come from MDX frontmatter in the public blog source repository. The site content index rejects dates later than the August 3, 2026 audit date.

When a search UI conflicts with the source frontmatter, correct the search or presentation layer rather than rewriting the canonical article history without evidence.

### Sitemap or robots issue

Check:

```text
https://bradleymatera.github.io/Office/robots.txt
https://bradleymatera.github.io/Office/sitemap.xml
```

The sitemap URL declared in `robots.txt` must match the Pages base URL.

### Daily Pages health workflow fails

The workflow checks:

- primary and secondary HTML pages
- shared CSS
- social preview
- sitemap
- robots
- RSS
- `llms.txt`
- page identity text
- PNG content type

A failure may mean:

- Pages did not publish
- a route was renamed without updating the workflow
- a file is missing
- GitHub Pages or the network had a temporary issue

The workflow retries HTTP requests, but an intermittent external outage can still fail a run. Inspect the failed step before changing site code.

## AWS deployment troubleshooting

### Deployment reports an S3 bucket naming error

The template does not force a physical bucket name. CloudFormation creates a unique name.

Avoid adding a fixed bucket name unless there is a documented naming, collision, and multi-environment strategy.

### SNS email never arrives after deployment

When `AlarmEmail` is supplied, AWS sends a subscription-confirmation email.

Check:

- inbox, spam, and quarantine
- SNS subscription status
- email address in the CloudFormation parameter
- topic ARN in stack outputs

Alarm notifications are not delivered until the subscription is confirmed.

### Upload succeeds but Lambda is not invoked

First compare the key with `UploadPrefix`.

Default expected path:

```text
incoming/sample.txt
```

An object outside `incoming/` should not trigger processing.

Then check:

1. bucket notification configuration
2. Lambda resource policy
3. stack resources
4. correct account and region
5. whether a retained bucket points to a deleted function

### Lambda runs but no DynamoDB record appears

1. inspect the structured log outcome
2. confirm `TABLE_NAME`
3. confirm table existence and region
4. check IAM permissions
5. check the failure queue
6. compare bucket, decoded key, version ID, ETag, and deterministic identity
7. determine whether the result was a safe `duplicate`

### Access denied on `HeadObject`

Check:

- bucket and object identity
- object version
- function role
- customer-managed KMS key permissions when applicable
- configuration drift

The generated S3 read policy includes versioned-object read permission. Do not replace it with unrestricted wildcard access without a documented requirement.

### Object key looks wrong

S3 notification keys are URL-encoded. The handler uses `unquote_plus`.

```text
incoming%2Fquarterly+report.pdf
```

becomes:

```text
incoming/quarterly report.pdf
```

### The same event appears twice

S3 notification delivery can repeat. The function creates a deterministic `RecordId` and uses a conditional write. The same identity is logged as `duplicate`.

### A replacement upload creates another record

The bucket has versioning enabled. A replacement object normally creates a new version ID and therefore a new metadata identity. That is expected and is different from duplicate delivery of the same event.

### Failure-queue alarm is active

Do not delete messages immediately.

Use the operations runbook:

1. preserve failure context
2. identify the exception
3. correct the root cause
4. check for an existing item
5. verify the referenced version still exists
6. replay safely
7. verify recovery
8. delete only after success

### Lambda throttle alarm is active

Investigate:

- concurrency limits
- sudden upload volume
- long execution duration
- retry traffic
- downstream latency

Do not raise concurrency automatically without understanding the traffic and downstream capacity.

### Stack deletion leaves resources behind

This is intentional for the bucket and table.

A retained versioned bucket may also retain its event-notification configuration. Inspect and remove a stale Lambda destination before reusing or deleting the bucket.

To delete a versioned S3 bucket, remove all object versions and delete markers. Preserve anything that still needs retention before cleanup.

## Claim and content troubleshooting

### A page sounds like production ownership

Compare the wording with:

- `docs/security-and-scope.md`
- `docs/interview-guide.md`
- `proof.html`
- the internship article

The safe description is training and capstone work in isolated environments, followed by a public reconstruction. Do not silently convert that into live enterprise ownership.

### A GitHub repository appears AWS-related but is not listed as proof

The proof page intentionally excludes:

- forks presented as original work
- design plans presented as deployed infrastructure
- resumes or cover letters presented as engineering implementation

Add a repository only when its role and authorship can be described accurately.
