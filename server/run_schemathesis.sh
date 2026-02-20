#!/usr/bin/env bash
# Run schemathesis pytest tests against the local server.
# Ensure the server is running at http://localhost:8080 (or set BASE_URL).

BASE=${BASE_URL:-http://localhost:8080}
PYTHONPATH=$(dirname "$0")/.. pytest -q server/tests/test_openapi_schemathesis.py -k "not slow" -o junit_family=xunit2
