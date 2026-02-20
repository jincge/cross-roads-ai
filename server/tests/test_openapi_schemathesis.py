import os
import schemathesis

# Load the OpenAPI schema from repository root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCHEMA_PATH = os.path.join(ROOT, "cross-road.yml")

schema = schemathesis.from_path(SCHEMA_PATH)

@schema.parametrize()
def test_api(case):
    # Base URL may be overridden via BASE_URL env var
    base_url = os.environ.get("BASE_URL", "http://localhost:8080")
    response = case.call(base_url=base_url)
    case.validate_response(response)
