PYTHON ?= python3
STACK_NAME ?= aws-serverless-metadata-workflow
AWS_REGION ?= us-east-1

.PHONY: install compile lint test site validate build check deploy outputs clean

install:
	$(PYTHON) -m pip install --upgrade -r requirements-dev.txt

compile:
	$(PYTHON) -m compileall -q src tests scripts

lint:
	ruff check src tests scripts

test:
	AWS_DEFAULT_REGION=$(AWS_REGION) AWS_EC2_METADATA_DISABLED=true TABLE_NAME=test-metadata-table \
		pytest --cov=src/metadata_extractor --cov-report=term-missing --cov-fail-under=85

site:
	$(PYTHON) scripts/validate_site.py

validate:
	sam validate --lint

build:
	sam build

check: compile lint test site validate build

deploy: check
	sam deploy --guided --stack-name $(STACK_NAME) --region $(AWS_REGION)

outputs:
	aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--region $(AWS_REGION) \
		--query 'Stacks[0].Outputs' \
		--output table

clean:
	rm -rf .aws-sam .pytest_cache .ruff_cache .coverage htmlcov
	find src tests scripts -type d -name __pycache__ -prune -exec rm -rf {} +
