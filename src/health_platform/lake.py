"""Talk to the data lake through the standard S3 API.

🍽️ The pantry. Same code works against real AWS S3: only the endpoint changes.
"""

import os
from pathlib import Path

import boto3


def s3_client():
    """S3 client for our local lake, using credentials from .env."""
    return boto3.client(
        "s3",
        endpoint_url=os.environ.get("LAKE_ENDPOINT", "http://127.0.0.1:8333"),
        aws_access_key_id=os.environ["LAKE_ACCESS_KEY"],
        aws_secret_access_key=os.environ["LAKE_SECRET_KEY"],
        region_name="us-east-1",  # required by the S3 API; ignored locally
    )


def upload_raw(path: str | Path, key: str, bucket: str = "raw") -> str:
    """Store a file in the lake exactly as delivered. Same key = overwrite (idempotent)."""
    s3_client().upload_file(str(path), bucket, key)
    return f"s3://{bucket}/{key}"
