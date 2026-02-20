import os
import schemathesis

# Load schema from repository root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCHEMA_PATH = os.path.join(ROOT, "cross-road.yml")

schema = schemathesis.openapi.from_path(SCHEMA_PATH)

@schema.parametrize()
def test_api(case):
    base_url = os.environ.get("BASE_URL", "http://localhost:8081")
    response = case.call(base_url=base_url)
    case.validate_response(response)
