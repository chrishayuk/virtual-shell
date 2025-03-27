"""
tests/virtual_shell/filesystem/providers/test_s3_storage_provider.py
"""
import json
import posixpath
import time
import pytest
from virtual_shell.filesystem.providers.s3 import S3StorageProvider
from virtual_shell.filesystem.node_info import FSNodeInfo

# -----------------------
# Dummy S3 Classes (same as before)
# -----------------------
class DummyBody:
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content.encode('utf-8') if isinstance(self.content, str) else self.content

class DummyPaginator:
    def __init__(self, objects):
        self.objects = objects

    def paginate(self, Bucket, Prefix, Delimiter=None):
        contents = []
        for key, obj in self.objects.items():
            if key.startswith(Prefix):
                contents.append({"Key": key, "Size": obj["Size"]})
        page = {"Contents": contents} if contents else {}
        yield page

class DummyS3Client:
    def __init__(self):
        self.objects = {}
        self.exceptions = type("DummyExceptions", (), {
            "NoSuchKey": Exception,
            "ClientError": Exception,
            "NoSuchBucket": Exception
        })

    def head_bucket(self, Bucket):
        return {}

    def create_bucket(self, Bucket):
        return {}

    def head_object(self, Bucket, Key):
        if Key not in self.objects:
            raise self.exceptions.NoSuchKey("Not found")
        return {}

    def put_object(self, Bucket, Key, Body):
        body = Body if isinstance(Body, str) else Body
        self.objects[Key] = {"Body": body, "Size": len(body.encode('utf-8')) if isinstance(body, str) else len(body)}
        return {}

    def get_object(self, Bucket, Key):
        if Key not in self.objects:
            raise self.exceptions.NoSuchKey("Not found")
        return {"Body": DummyBody(self.objects[Key]["Body"])}

    def delete_object(self, Bucket, Key):
        if Key in self.objects:
            del self.objects[Key]
        return {}

    def list_objects_v2(self, Bucket, Prefix, MaxKeys=None):
        contents = []
        for key, obj in self.objects.items():
            if key.startswith(Prefix):
                contents.append({"Key": key, "Size": obj["Size"]})
        return {"Contents": contents} if contents else {}

    def get_paginator(self, operation_name):
        return DummyPaginator(self.objects)

    def delete_objects(self, Bucket, Delete):
        for obj in Delete["Objects"]:
            key = obj["Key"]
            if key in self.objects:
                del self.objects[key]
        return {}

# -----------------------
# Pytest Fixtures for S3 Provider
# -----------------------

@pytest.fixture
def dummy_s3_client():
    return DummyS3Client()

@pytest.fixture
def provider(dummy_s3_client):
    # Force a non-empty prefix to avoid the None issue.
    prov = S3StorageProvider(bucket_name="dummy-bucket", prefix="dummy")
    prov.client = dummy_s3_client
    prov.resource = None
    # Create root node with the given prefix.
    root_info = FSNodeInfo("", True)
    root_key = prov._get_node_key("/")
    root_data = json.dumps(root_info.to_dict())
    dummy_s3_client.put_object(Bucket="dummy-bucket", Key=root_key, Body=root_data)
    return prov

def test_initialize_s3(provider, dummy_s3_client):
    root_info = provider.get_node_info("/")
    assert root_info is not None
    assert root_info.name == ""
    assert root_info.is_dir is True

def test_create_node_file(provider):
    home_info = FSNodeInfo("home", True, parent_path="/")
    assert provider.create_node(home_info) is True
    file_info = FSNodeInfo("test.txt", False, parent_path="/home")
    result_file = provider.create_node(file_info)
    assert result_file is True
    stored = provider.get_node_info("/home/test.txt")
    assert stored is not None
    assert stored.name == "test.txt"
    content = provider.read_file("/home/test.txt")
    assert content == ""

def test_create_node_failure(provider):
    orphan = FSNodeInfo("orphan.txt", False, parent_path="/nonexistent")
    result = provider.create_node(orphan)
    assert result is False

def test_list_directory(provider):
    docs_info = FSNodeInfo("docs", True, parent_path="/")
    assert provider.create_node(docs_info) is True
    file1 = FSNodeInfo("a.txt", False, parent_path="/docs")
    file2 = FSNodeInfo("b.txt", False, parent_path="/docs")
    assert provider.create_node(file1) is True
    assert provider.create_node(file2) is True
    listing = provider.list_directory("/docs")
    assert set(listing) == {"a.txt", "b.txt"}

def test_write_and_read_file(provider):
    logs_info = FSNodeInfo("logs", True, parent_path="/")
    assert provider.create_node(logs_info) is True
    file_info = FSNodeInfo("log.txt", False, parent_path="/logs")
    assert provider.create_node(file_info) is True
    text = "Hello S3!"
    assert provider.write_file("/logs/log.txt", text) is True
    read_text = provider.read_file("/logs/log.txt")
    assert read_text == text

def test_delete_node_file(provider):
    temp_info = FSNodeInfo("temp", True, parent_path="/")
    assert provider.create_node(temp_info) is True
    file_info = FSNodeInfo("delete_me.txt", False, parent_path="/temp")
    assert provider.create_node(file_info) is True
    assert provider.get_node_info("/temp/delete_me.txt") is not None
    result = provider.delete_node("/temp/delete_me.txt")
    assert result is True
    assert provider.get_node_info("/temp/delete_me.txt") is None

def test_delete_node_directory_nonempty(provider):
    dir_info = FSNodeInfo("nonempty", True, parent_path="/")
    assert provider.create_node(dir_info) is True
    child_info = FSNodeInfo("child.txt", False, parent_path="/nonempty")
    assert provider.create_node(child_info) is True
    result = provider.delete_node("/nonempty")
    assert result is False

def test_get_storage_stats(provider):
    file_info = FSNodeInfo("file1.txt", False, parent_path="/")
    assert provider.create_node(file_info) is True
    text = "S3 storage stats"
    assert provider.write_file("/file1.txt", text) is True
    stats = provider.get_storage_stats()
    assert isinstance(stats, dict)
    # Expect at least one file.
    assert stats["file_count"] >= 1
    expected_size = len(text.encode('utf-8'))
    assert stats["total_size_bytes"] >= expected_size

def test_cleanup(provider, dummy_s3_client):
    tmp_info = FSNodeInfo("tmp", True, parent_path="/")
    assert provider.create_node(tmp_info) is True
    file_info = FSNodeInfo("junk.txt", False, parent_path="/tmp")
    assert provider.create_node(file_info) is True
    content = "temporary S3 data"
    assert provider.write_file("/tmp/junk.txt", content) is True
    stats_before = provider.get_storage_stats()
    size_before = stats_before["total_size_bytes"]
    result = provider.cleanup()
    assert result["files_removed"] >= 1
    assert result["bytes_freed"] > 0
    assert provider.get_node_info("/tmp/junk.txt") is None
