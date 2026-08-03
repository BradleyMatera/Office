# Testing and Validation

## Validation philosophy

This repository treats the Lambda function, AWS infrastructure, public documentation, SEO surface, and live GitHub Pages deployment as one product.

Validation therefore asks more than “does the function run?” It asks:

- does the processing logic normalize the right fields?
- are repeated event identities safe?
- do unexpected failures reach the retry path?
- does the infrastructure template express the intended security and operational controls?
- do the public pages link to real files and canonical articles?
- does structured metadata parse?
- do the diagrams remain accessible?
- does the live Pages site continue serving the routes used by resumes?
- do the words remain consistent with the verified internship scope?

## Current local test result

An independent local audit completed on August 3, 2026 produced:

- **11 passing tests**
- **100% statement coverage**
- **100% branch coverage**

This is a dated audit result, not a permanent guarantee. The repository CI enforces a minimum of 85% coverage so future changes cannot silently remove most of the test protection.

## Unit-test coverage

`tests/test_app.py` covers:

1. a normal versioned S3 object-created event
2. URL-decoding of object keys
3. version-aware `HeadObject` arguments
4. required and optional metadata normalization
5. custom S3 user metadata
6. checksum storage
7. deterministic record identity shape
8. safe duplicate handling after `ConditionalCheckFailedException`
9. propagation of unexpected DynamoDB errors for Lambda retry
10. an unversioned object with fallback fields
11. rejection of a non-S3 event source
12. rejection of an unsupported event major version
13. rejection of an invalid event version
14. rejection of an empty event record list
15. required `TABLE_NAME` configuration
16. lazy AWS SDK client and table reuse
17. timestamp helper fallback behavior

Several assertions are grouped into the 11 test functions. The scenario count is therefore larger than the test-function count.

## Run the local verification suite

Install dependencies:

```bash
make install
```

Run every local check:

```bash
make check
```

The aggregate command performs:

```text
compile -> lint -> unit tests and coverage -> static-site validation -> SAM lint -> SAM build
```

Individual targets:

```bash
make compile
make lint
make test
make site
make validate
make build
```

## Python compilation

```bash
python -m compileall -q src tests scripts
```

This catches syntax errors in the Lambda, tests, and production-site validator before later steps run.

## Ruff linting

```bash
ruff check src tests scripts
```

The configuration targets Python 3.12 and checks:

- pycodestyle errors
- Pyflakes
- import sorting
- Python-upgrade rules
- common bug patterns
- simplification rules

## Unit tests and coverage

```bash
AWS_DEFAULT_REGION=us-east-1 \
AWS_EC2_METADATA_DISABLED=true \
TABLE_NAME=test-metadata-table \
pytest \
  --cov=src/metadata_extractor \
  --cov-report=term-missing \
  --cov-fail-under=85
```

The tests use fake S3 and DynamoDB objects. They do not require an AWS account and do not make network calls.

## Static-site validation

```bash
python scripts/validate_site.py
```

The validator uses only the Python standard library and checks:

### Page structure

- expected public HTML pages exist
- `lang="en"`
- unique page titles
- one meta description
- one canonical URL on public indexable pages
- one non-empty `h1`
- one main landmark
- a skip link
- no duplicate element IDs

### Accessibility and assets

- every image has `alt`
- every local image and stylesheet target exists
- SVG diagrams contain `<title>` and `<desc>`
- internal fragment links resolve
- local links do not escape the repository root

### SEO and structured data

- JSON-LD parses as JSON
- canonical URLs use the Pages base URL
- local Open Graph images exist
- canonical URLs are unique across pages
- page titles are unique
- `robots.txt` names the canonical sitemap
- `sitemap.xml` and `rss.xml` parse as XML
- `site.webmanifest` parses as JSON

### Content governance

- `data/aws-content.json` parses
- canonical article IDs and URLs are unique
- article dates do not exceed the audit date
- every article illustration exists
- required production files such as `llms.txt`, `humans.txt`, `robots.txt`, the manifest, and shared CSS are present

The validator checks local repository integrity. It does not make external network requests and does not claim that every external website is reachable at test time.

## AWS SAM validation

```bash
sam validate --lint
```

This checks the SAM and CloudFormation template against the available schema and lint rules.

## AWS SAM build

```bash
sam build
```

This confirms that the function source and infrastructure can be assembled into a SAM build output.

A successful build is not the same as a successful AWS deployment. Deployment still requires authorized AWS credentials, CloudFormation permissions, resource availability, and parameter review.

## GitHub Actions validation workflow

`.github/workflows/validate.yml` runs on:

- pushes to `main`
- pull requests targeting `main`
- manual dispatch

It performs:

1. checkout
2. Python 3.12 setup
3. dependency installation
4. Python compilation
5. Ruff linting
6. unit tests and coverage
7. static-site validation
8. AWS SAM template linting
9. AWS SAM build

The workflow uses concurrency control so a newer run for the same ref cancels an obsolete run.

## Live GitHub Pages health workflow

`.github/workflows/site-health.yml` runs daily and can be triggered manually.

It requests critical public resources including:

- the primary workflow page
- AWS writing hub
- proof map
- verified-source page
- design-system page
- shared CSS
- social preview PNG
- sitemap
- robots file
- RSS feed
- `llms.txt`

It also checks for page-specific identity text and verifies that the social image is served as `image/png`.

This workflow tests public availability. It does not test an AWS stack because no AWS account is connected to the public Pages site.

## Deployed AWS integration validation

After an intentional deployment:

### 1. Confirm stack identity

```bash
aws sts get-caller-identity
make outputs
```

### 2. Upload under the configured prefix

```bash
printf 'metadata workflow test\n' > sample.txt
aws s3 cp sample.txt s3://YOUR_UPLOAD_BUCKET/incoming/sample.txt \
  --content-type text/plain \
  --metadata source=integration-test
```

### 3. Confirm Lambda execution

```bash
aws logs tail /aws/lambda/YOUR_FUNCTION_NAME \
  --region us-east-1 \
  --since 10m \
  --follow
```

### 4. Confirm stored metadata

```bash
aws dynamodb scan \
  --region us-east-1 \
  --table-name YOUR_METADATA_TABLE \
  --max-items 10
```

A scan is acceptable for a small deployment verification. It is not presented as the production access pattern for a high-volume application.

### 5. Confirm prefix filtering

Upload a harmless object outside the configured prefix. It should not invoke the extractor.

### 6. Confirm alert readiness

- confirm the SNS email subscription when configured
- inspect the three CloudWatch alarms
- confirm the failure queue URL

Do not deliberately create uncontrolled production failures merely to prove an alarm exists.

## Validation boundaries

The following statements remain separate:

- **unit tests passed** means the tested Python behavior passed with fake clients
- **SAM validated and built** means the application template and package passed local tooling
- **Pages health passed** means the public static routes responded
- **AWS integration passed** means an authorized deployed stack processed a real test object

Do not combine these into the unsupported statement “production is fully verified” unless a real deployed environment was tested and the evidence was recorded.

## Why this matters

The repository is intended to answer technical and recruiter questions under scrutiny. Testing the code but leaving broken pages, stale claims, invalid structured data, missing diagrams, or silent operational alarms would weaken the project.

The explanation is part of the system and receives its own validation contract.
