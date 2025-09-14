#!/usr/bin/env python3
"""
Test S3 API versions and capabilities to determine what works with Tigris.
"""

import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get credentials from environment
access_key = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
endpoint_url = os.environ.get("AWS_ENDPOINT_URL_S3")
bucket_name = os.environ.get("S3_BUCKET_NAME", "").strip('"')
region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

print("=" * 60)
print("S3 API Version and Capability Testing")
print("=" * 60)
print(f"Endpoint: {endpoint_url}")
print(f"Bucket: {bucket_name}")
print(f"Region: {region}")
print(f"Access Key: {access_key[:10]}..." if access_key else "Access Key: NOT SET")
print("=" * 60)
print()

def test_client_config(signature_version, addressing_style="auto", use_ssl=True):
    """Test a specific client configuration."""
    print(f"\n--- Testing: signature={signature_version}, addressing={addressing_style}, ssl={use_ssl} ---")
    
    try:
        # Create config
        config = Config(
            signature_version=signature_version,
            s3={'addressing_style': addressing_style},
            retries={'max_attempts': 1}
        )
        
        # Create client
        client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=config,
            use_ssl=use_ssl
        )
        
        results = {}
        
        # Test 1: List Buckets
        try:
            response = client.list_buckets()
            results['list_buckets'] = f"✓ ({len(response.get('Buckets', []))} buckets)"
            bucket_names = [b['Name'] for b in response.get('Buckets', [])]
            if bucket_names:
                print(f"  Buckets found: {', '.join(bucket_names)}")
        except Exception as e:
            results['list_buckets'] = f"✗ {type(e).__name__}: {str(e)[:50]}"
        
        # Test 2: Head Bucket
        try:
            client.head_bucket(Bucket=bucket_name)
            results['head_bucket'] = "✓"
        except Exception as e:
            error_code = e.response.get('Error', {}).get('Code', '') if hasattr(e, 'response') else ''
            results['head_bucket'] = f"✗ {error_code or type(e).__name__}"
        
        # Test 3: List Objects (v1)
        try:
            response = client.list_objects(Bucket=bucket_name, MaxKeys=1)
            results['list_objects_v1'] = f"✓ ({len(response.get('Contents', []))} objects)"
        except Exception as e:
            error_code = e.response.get('Error', {}).get('Code', '') if hasattr(e, 'response') else ''
            results['list_objects_v1'] = f"✗ {error_code or type(e).__name__}"
        
        # Test 4: List Objects v2
        try:
            response = client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            results['list_objects_v2'] = f"✓ ({len(response.get('Contents', []))} objects)"
        except Exception as e:
            error_code = e.response.get('Error', {}).get('Code', '') if hasattr(e, 'response') else ''
            results['list_objects_v2'] = f"✗ {error_code or type(e).__name__}"
        
        # Test 5: Put Object
        test_key = "_test_api_version.txt"
        try:
            client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=b"Test content for API version detection"
            )
            results['put_object'] = "✓"
            
            # Test 6: Get Object
            try:
                response = client.get_object(Bucket=bucket_name, Key=test_key)
                content = response['Body'].read()
                results['get_object'] = f"✓ ({len(content)} bytes)"
            except Exception as e:
                results['get_object'] = f"✗ {type(e).__name__}"
            
            # Test 7: Head Object
            try:
                client.head_object(Bucket=bucket_name, Key=test_key)
                results['head_object'] = "✓"
            except Exception as e:
                results['head_object'] = f"✗ {type(e).__name__}"
            
            # Test 8: Delete Object
            try:
                client.delete_object(Bucket=bucket_name, Key=test_key)
                results['delete_object'] = "✓"
            except Exception as e:
                results['delete_object'] = f"✗ {type(e).__name__}"
                
        except Exception as e:
            error_code = e.response.get('Error', {}).get('Code', '') if hasattr(e, 'response') else ''
            results['put_object'] = f"✗ {error_code or type(e).__name__}"
            results['get_object'] = "N/A"
            results['head_object'] = "N/A"
            results['delete_object'] = "N/A"
        
        # Test 9: Multipart Upload
        try:
            response = client.create_multipart_upload(
                Bucket=bucket_name,
                Key="_test_multipart.txt"
            )
            upload_id = response['UploadId']
            client.abort_multipart_upload(
                Bucket=bucket_name,
                Key="_test_multipart.txt",
                UploadId=upload_id
            )
            results['multipart_upload'] = "✓"
        except Exception as e:
            results['multipart_upload'] = f"✗ {type(e).__name__}"
        
        # Test 10: Get Bucket Location
        try:
            response = client.get_bucket_location(Bucket=bucket_name)
            results['get_bucket_location'] = f"✓ ({response.get('LocationConstraint', 'us-east-1')})"
        except Exception as e:
            results['get_bucket_location'] = f"✗ {type(e).__name__}"
        
        # Test 11: Get Bucket ACL
        try:
            response = client.get_bucket_acl(Bucket=bucket_name)
            results['get_bucket_acl'] = "✓"
        except Exception as e:
            results['get_bucket_acl'] = f"✗ {type(e).__name__}"
        
        # Print results
        print("\n  Results:")
        for operation, result in results.items():
            print(f"    {operation:20} : {result}")
        
        # Calculate success rate
        successes = sum(1 for r in results.values() if r.startswith("✓"))
        total = len(results)
        print(f"\n  Success rate: {successes}/{total} operations")
        
        return successes > 0
        
    except Exception as e:
        print(f"  Failed to create client: {type(e).__name__}: {e}")
        return False

# Test different configurations
configs_to_test = [
    # Signature versions
    ("s3v4", "auto", True),      # Modern S3 v4 signature
    ("s3v4", "path", True),       # Path-style addressing
    ("s3v4", "virtual", True),    # Virtual-hosted-style
    ("s3", "auto", True),         # Legacy S3 signature
    ("s3", "path", True),         # Legacy with path-style
    # Without SSL (some services require this)
    ("s3v4", "path", False),
    ("s3", "path", False),
]

print("\n" + "=" * 60)
print("Testing Different S3 Client Configurations")
print("=" * 60)

best_config = None
best_score = 0

for sig_ver, addr_style, use_ssl in configs_to_test:
    if test_client_config(sig_ver, addr_style, use_ssl):
        # Count successful operations
        config = Config(
            signature_version=sig_ver,
            s3={'addressing_style': addr_style}
        )
        client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=config,
            use_ssl=use_ssl
        )
        
        score = 0
        for op in ['list_buckets', 'list_objects_v2', 'put_object', 'get_object']:
            try:
                if op == 'list_buckets':
                    client.list_buckets()
                elif op == 'list_objects_v2':
                    client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                elif op == 'put_object':
                    client.put_object(Bucket=bucket_name, Key="_test.txt", Body=b"test")
                elif op == 'get_object':
                    try:
                        client.get_object(Bucket=bucket_name, Key="_test.txt")
                    except:
                        pass
                score += 1
            except:
                pass
        
        if score > best_score:
            best_score = score
            best_config = (sig_ver, addr_style, use_ssl)

print("\n" + "=" * 60)
print("Recommendation")
print("=" * 60)

if best_config:
    sig_ver, addr_style, use_ssl = best_config
    print(f"Best configuration for {endpoint_url}:")
    print(f"  - Signature Version: {sig_ver}")
    print(f"  - Addressing Style: {addr_style}")
    print(f"  - Use SSL: {use_ssl}")
    print(f"  - Operations working: {best_score}/4 core operations")
    print()
    print("Suggested boto3 configuration:")
    print(f"""
from botocore.config import Config

config = Config(
    signature_version='{sig_ver}',
    s3={{'addressing_style': '{addr_style}'}},
    retries={{'max_attempts': 3, 'mode': 'standard'}}
)

client = boto3.client(
    's3',
    endpoint_url='{endpoint_url}',
    config=config,
    use_ssl={use_ssl}
)
""")
else:
    print("No working configuration found. Please check:")
    print("  1. Credentials are correct")
    print("  2. Bucket exists and you have access")
    print("  3. Endpoint URL is correct")
    print("  4. Network connectivity to the endpoint")