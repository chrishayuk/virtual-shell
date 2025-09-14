#!/usr/bin/env python3
"""
Test Tigris bucket operations - list, create, and permissions.
"""

import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Get credentials from environment
access_key = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
endpoint_url = os.environ.get("AWS_ENDPOINT_URL_S3")
bucket_name = os.environ.get("S3_BUCKET_NAME", "").strip('"')
region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

print("=" * 60)
print("Tigris Bucket Testing")
print("=" * 60)
print(f"Endpoint: {endpoint_url}")
print(f"Current bucket name: {bucket_name}")
print(f"Access Key: {access_key[:10]}..." if access_key else "Access Key: NOT SET")
print("=" * 60)
print()

# Create config
config = Config(
    signature_version='s3v4',
    s3={'addressing_style': 'path'},
    retries={'max_attempts': 3}
)

# Create client
client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region,
    config=config
)

# Test 1: List all buckets
print("1. Listing all buckets:")
try:
    response = client.list_buckets()
    buckets = response.get('Buckets', [])
    for bucket in buckets:
        print(f"   - {bucket['Name']} (created: {bucket.get('CreationDate', 'N/A')})")
        
        # Try to get bucket info
        print(f"     Testing access to {bucket['Name']}:")
        
        # Try list objects
        try:
            resp = client.list_objects_v2(Bucket=bucket['Name'], MaxKeys=1)
            obj_count = resp.get('KeyCount', 0)
            print(f"       list_objects_v2: ✓ ({obj_count} objects)")
        except Exception as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown') if hasattr(e, 'response') else str(e)
            print(f"       list_objects_v2: ✗ {error_code}")
        
        # Try put object
        try:
            client.put_object(
                Bucket=bucket['Name'],
                Key='_test_permission.txt',
                Body=b'test'
            )
            print(f"       put_object: ✓")
            # Clean up
            client.delete_object(Bucket=bucket['Name'], Key='_test_permission.txt')
        except Exception as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown') if hasattr(e, 'response') else str(e)
            print(f"       put_object: ✗ {error_code}")
            
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 2: Try to create a new bucket with a unique name
new_bucket_name = f"test-{uuid.uuid4().hex[:8]}"
print(f"2. Attempting to create new bucket: {new_bucket_name}")
try:
    response = client.create_bucket(Bucket=new_bucket_name)
    print(f"   ✓ Successfully created bucket: {new_bucket_name}")
    
    # Test operations on new bucket
    print(f"   Testing operations on new bucket:")
    
    # List objects
    try:
        client.list_objects_v2(Bucket=new_bucket_name, MaxKeys=1)
        print(f"     list_objects_v2: ✓")
    except Exception as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown') if hasattr(e, 'response') else str(e)
        print(f"     list_objects_v2: ✗ {error_code}")
    
    # Put object
    try:
        client.put_object(
            Bucket=new_bucket_name,
            Key='test.txt',
            Body=b'Hello from test'
        )
        print(f"     put_object: ✓")
    except Exception as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown') if hasattr(e, 'response') else str(e)
        print(f"     put_object: ✗ {error_code}")
    
    # Get object
    try:
        response = client.get_object(Bucket=new_bucket_name, Key='test.txt')
        content = response['Body'].read()
        print(f"     get_object: ✓ (got {len(content)} bytes)")
    except Exception as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown') if hasattr(e, 'response') else str(e)
        print(f"     get_object: ✗ {error_code}")
    
    # Clean up - delete the test bucket
    try:
        # First delete all objects
        response = client.list_objects_v2(Bucket=new_bucket_name)
        for obj in response.get('Contents', []):
            client.delete_object(Bucket=new_bucket_name, Key=obj['Key'])
        # Then delete bucket
        client.delete_bucket(Bucket=new_bucket_name)
        print(f"   ✓ Cleaned up test bucket")
    except Exception as e:
        print(f"   Note: Could not clean up test bucket: {e}")
        
except Exception as e:
    error_code = e.response.get('Error', {}).get('Code', 'Unknown') if hasattr(e, 'response') else str(e)
    print(f"   ✗ Could not create bucket: {error_code}")
    if 'InvalidBucketName' in str(e):
        print(f"   Note: Bucket name format issue. Tigris may have specific naming requirements.")

print()

# Test 3: Get more info about the configured bucket
print(f"3. Detailed error analysis for bucket '{bucket_name}':")

# Try different operations to understand the permission model
operations = [
    ('HEAD bucket', lambda: client.head_bucket(Bucket=bucket_name)),
    ('GET bucket location', lambda: client.get_bucket_location(Bucket=bucket_name)),
    ('GET bucket ACL', lambda: client.get_bucket_acl(Bucket=bucket_name)),
    ('LIST objects v1', lambda: client.list_objects(Bucket=bucket_name, MaxKeys=1)),
    ('LIST objects v2', lambda: client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)),
    ('PUT object', lambda: client.put_object(Bucket=bucket_name, Key='test.txt', Body=b'test')),
]

for op_name, op_func in operations:
    try:
        result = op_func()
        print(f"   {op_name:20} : ✓")
    except Exception as e:
        if hasattr(e, 'response'):
            error = e.response.get('Error', {})
            code = error.get('Code', 'Unknown')
            msg = error.get('Message', '')[:50]
            print(f"   {op_name:20} : ✗ {code} - {msg}")
        else:
            print(f"   {op_name:20} : ✗ {str(e)[:50]}")

print()
print("=" * 60)
print("Recommendations:")
print("=" * 60)

print("""
Based on the tests above:

1. If you can create and use new buckets: 
   - Create a new bucket with a unique name
   - Use that bucket for your application

2. If bucket 'chuk-bucket-10' shows AccessDenied:
   - Check if the bucket belongs to a different account/project
   - Verify the access keys have permissions for this bucket
   - Contact Tigris support to verify bucket ownership

3. If all operations fail:
   - Verify credentials are active and not expired
   - Check if there are IP restrictions or other security policies
   - Try regenerating the access keys in Tigris console
""")