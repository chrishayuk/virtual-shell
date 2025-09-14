#!/usr/bin/env python3
"""Test Tigris S3 connection."""

import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment
access_key = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
endpoint_url = os.environ.get("AWS_ENDPOINT_URL_S3")
bucket_name = os.environ.get("S3_BUCKET_NAME", "").strip('"')
region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

print(f"Testing Tigris connection:")
print(f"  Endpoint: {endpoint_url}")
print(f"  Bucket: {bucket_name}")
print(f"  Region: {region}")
print(f"  Access Key: {access_key[:10]}..." if access_key else "  Access Key: NOT SET")
print()

# Create S3 client
try:
    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )
    
    # Try to list buckets
    print("Listing buckets:")
    response = s3_client.list_buckets()
    for bucket in response.get("Buckets", []):
        print(f"  - {bucket['Name']}")
    
    # Try to check if our bucket exists
    print(f"\nChecking bucket '{bucket_name}':")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"  ✓ Bucket '{bucket_name}' exists and is accessible")
    except Exception as e:
        print(f"  ✗ Error accessing bucket '{bucket_name}': {e}")
        
        # Try to create the bucket
        print(f"\nAttempting to create bucket '{bucket_name}':")
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"  ✓ Bucket '{bucket_name}' created successfully")
        except Exception as create_error:
            print(f"  ✗ Error creating bucket: {create_error}")
    
    # Try to list objects in the bucket
    print(f"\nListing objects in '{bucket_name}':")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=10)
        objects = response.get("Contents", [])
        if objects:
            for obj in objects:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("  (bucket is empty)")
    except Exception as e:
        print(f"  ✗ Error listing objects: {e}")
        
except Exception as e:
    print(f"Error creating S3 client: {e}")