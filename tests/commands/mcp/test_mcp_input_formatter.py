"""
tests/commands/mcp/test_mcp_input_formatter.py - Tests for MCP input formatter

Tests the functionality of formatting user input for MCP tools based on their schemas.
"""

from chuk_virtual_shell.commands.mcp.mcp_input_formatter import format_mcp_input


def test_format_mcp_input_no_schema():
    """Test formatting when no schema is provided"""
    args = ["arg1", "arg2", "arg3"]
    result = format_mcp_input(args, None)
    assert result == {"args": args}


def test_format_mcp_input_empty_properties():
    """Test formatting when schema has no properties"""
    args = ["arg1", "arg2"]
    schema = {"type": "object", "properties": {}}
    result = format_mcp_input(args, schema)
    assert result == {}


def test_format_mcp_input_single_required_query():
    """Test formatting when there's a single required 'query' property"""
    args = ["SELECT", "*", "FROM", "users"]
    schema = {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "SQL query"}},
        "required": ["query"],
    }
    result = format_mcp_input(args, schema)
    assert result == {"query": "SELECT * FROM users"}


def test_format_mcp_input_single_required_non_query():
    """Test formatting when there's a single required property that's not 'query'"""
    args = ["my_table"]
    schema = {
        "type": "object",
        "properties": {"table_name": {"type": "string", "description": "Table name"}},
        "required": ["table_name"],
    }
    result = format_mcp_input(args, schema)
    assert result == {"table_name": "my_table"}


def test_format_mcp_input_single_required_multiple_args():
    """Test formatting when there's a single required property and multiple args"""
    args = ["value1", "value2", "value3"]
    schema = {
        "type": "object",
        "properties": {"field": {"type": "string"}},
        "required": ["field"],
    }
    result = format_mcp_input(args, schema)
    # Should only take the first argument for non-query fields
    assert result == {"field": "value1"}


def test_format_mcp_input_query_property_not_required():
    """Test formatting when 'query' property exists but is not required"""
    args = ["SELECT", "COUNT(*)", "FROM", "orders"]
    schema = {
        "type": "object",
        "properties": {"query": {"type": "string"}, "limit": {"type": "number"}},
        "required": [],
    }
    result = format_mcp_input(args, schema)
    assert result == {"query": "SELECT COUNT(*) FROM orders"}


def test_format_mcp_input_no_args_with_required():
    """Test formatting when no args are provided but there are required fields"""
    args = []
    schema = {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    }
    result = format_mcp_input(args, schema)
    # Should return empty query since no args provided
    assert result == {"args": []}


def test_format_mcp_input_multiple_required_properties():
    """Test formatting when there are multiple required properties"""
    args = ["value1", "value2"]
    schema = {
        "type": "object",
        "properties": {"field1": {"type": "string"}, "field2": {"type": "string"}},
        "required": ["field1", "field2"],
    }
    result = format_mcp_input(args, schema)
    # Falls back to default formatting since multiple required fields
    assert result == {"args": args}


def test_format_mcp_input_complex_query():
    """Test formatting with a complex SQL query"""
    args = [
        "SELECT",
        "u.name,",
        "COUNT(o.id)",
        "FROM",
        "users",
        "u",
        "JOIN",
        "orders",
        "o",
        "ON",
        "u.id=o.user_id",
        "GROUP",
        "BY",
        "u.name",
    ]
    schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "SQL query to execute"}
        },
        "required": ["query"],
    }
    result = format_mcp_input(args, schema)
    expected_query = "SELECT u.name, COUNT(o.id) FROM users u JOIN orders o ON u.id=o.user_id GROUP BY u.name"
    assert result == {"query": expected_query}


def test_format_mcp_input_empty_args_empty_properties():
    """Test formatting when both args and properties are empty"""
    args = []
    schema = {"type": "object", "properties": {}}
    result = format_mcp_input(args, schema)
    assert result == {}
