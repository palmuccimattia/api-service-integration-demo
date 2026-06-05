"""Example S3 configuration for demo scripts."""

import os


def get_bucket_name() -> str:
    return os.getenv("REPORTS_BUCKET_NAME", "demo-api-reports-bucket")
