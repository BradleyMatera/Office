# Testing and Validation

## Validation goals

For this workflow, validation means more than just confirming that a function runs. It means checking the whole chain of behavior:

- does an upload trigger processing?
- is the metadata extracted correctly?
- is the record normalized consistently?
- is the record persisted successfully?
- can the result be explained and communicated clearly?

## Logical validation steps

### 1. Upload test

Confirm that placing a file in the intake bucket produces the expected event-driven behavior.

### 2. Lambda execution check

Confirm that the function is invoked and that execution behavior matches the expected path.

### 3. Metadata accuracy check

Compare stored metadata fields against the uploaded file’s known characteristics.

### 4. Persistence check

Verify that a structured item is written to DynamoDB with the expected attributes.

### 5. Presentation check

Confirm that the public-facing explanation, diagrams, and wording remain accurate and do not overstate scope.

## Public portfolio validation

For the public repo itself, the main checks are:

- diagrams load correctly
- documentation links work
- the Pages-ready site renders clearly
- the wording stays truthful and consistent with the actual project scope

## Why this matters

Technical work is stronger when the explanation is tested too. A project that is architecturally sound but poorly communicated will not perform as well in interviews or technical reviews.
