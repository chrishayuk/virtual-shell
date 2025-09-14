#!/usr/bin/env python3
"""Verify that files are actually stored in Tigris S3."""

import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

# Get credentials
access_key = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
endpoint_url = os.environ.get("AWS_ENDPOINT_URL_S3")
bucket_name = os.environ.get("S3_BUCKET_NAME", "").strip('"')
region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

print(f"Checking bucket: {bucket_name}")
print(f"Endpoint: {endpoint_url}")
print()

# Create S3 client
config = Config(signature_version="s3v4", s3={"addressing_style": "path"})

client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region,
    config=config,
)

# List all objects in the bucket
try:
    response = client.list_objects_v2(Bucket=bucket_name)
    objects = response.get("Contents", [])

    if objects:
        print(f"Found {len(objects)} objects in bucket:")
        for obj in objects:
            print(
                f"  - {obj['Key']} ({obj['Size']} bytes, modified: {obj['LastModified']})"
            )

            # Try to get content of small text files
            if obj["Size"] < 1000 and not obj["Key"].endswith(".json"):
                try:
                    resp = client.get_object(Bucket=bucket_name, Key=obj["Key"])
                    content = resp["Body"].read().decode("utf-8")
                    print(f"    Content: {content[:100]}")
                except Exception as e:
                    print(f"    Could not read content: {e}")
    else:
        print("Bucket is empty")

except Exception as e:
    print(f"Error: {e}")
