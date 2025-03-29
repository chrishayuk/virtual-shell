# tests/test_mcp_config_loader.py
from chuk_virtual_shell.sandbox.loader.mcp_config_loader import load_mcp_servers

def test_load_mcp_servers_valid():
    config = {
        "mcp_servers": [
            {"config_path": "config.json", "server_name": "test_server"}
        ]
    }
    servers = load_mcp_servers(config)
    assert len(servers) == 1
    assert servers[0]["server_name"] == "test_server"

def test_load_mcp_servers_invalid():
    config = {
        "mcp_servers": [
            {"config_path": "config.json"}  # Missing server_name
        ]
    }
    servers = load_mcp_servers(config)
    assert len(servers) == 0
