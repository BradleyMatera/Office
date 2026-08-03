PYTHON ?= python3
STACK_NAME ?= aws-serverless-metadata-workflow
AWS_REGION ?= us-east-1

.PHONY: install lint test validate build deploy outputs clean

install:
	$(PYTHON) -m pip install --upgrade -r requirements-dev.txt

lint:
	ruff check src tests

test:
	AWS_DEFAULT_REGION=$(AWS_REGION) AWS_EC2_METADATA_DISABLED=true TABLE_NAME=test-metadata-table \
		pytest --cov=src/metadata_extractor --cov-report=term-missing --cov-fail-under=85

validate:
	sam validate --lint

build:
	sam build

deploy: build
	sam deploy --guided --stack-name $(STACK_NAME) --region $(AWS_REGION)

outputs:
	aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--region $(AWS_REGION) \
		--query 'Stacks[0].Outputs' \
		--output table

clean:
	rm -rf .aws-sam .pytest_cache .coverage htmlcov
