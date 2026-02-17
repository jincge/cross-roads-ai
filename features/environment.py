import os, sys

# Ensure the package in `python/` is importable during behave runs
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SDK_PATH = os.path.join(ROOT, "python")
if SDK_PATH not in sys.path:
    sys.path.insert(0, SDK_PATH)


def before_all(context):
    """Behave hook: provide the base URL for API requests.

    Use API_BASE_URL env var to override (e.g. http://localhost:8080).
    """
    context.base_url = os.environ.get("API_BASE_URL", "http://localhost:8080")
