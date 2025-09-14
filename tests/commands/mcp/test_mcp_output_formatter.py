"""
tests/commands/mcp/test_mcp_output_formatter.py - Tests for MCP output formatter

Tests the functionality of parsing and formatting MCP tool responses.
"""

import json
from chuk_virtual_shell.commands.mcp.mcp_output_formatter import (
    parse_mcp_response,
    format_mcp_result,
    _attempt_json_load,
    _attempt_literal_eval,
    _format_list_result,
    _format_tabular_data,
)


# Tests for _attempt_json_load
def test_attempt_json_load_valid():
    """Test JSON loading with valid JSON string"""
    result = _attempt_json_load('{"key": "value", "number": 42}')
    assert result == {"key": "value", "number": 42}


def test_attempt_json_load_invalid():
    """Test JSON loading with invalid JSON string"""
    result = _attempt_json_load("not valid json")
    assert result is None


def test_attempt_json_load_none():
    """Test JSON loading with None input"""
    result = _attempt_json_load(None)
    assert result is None


# Tests for _attempt_literal_eval
def test_attempt_literal_eval_valid():
    """Test literal_eval with valid Python literal"""
    result = _attempt_literal_eval("{'key': 'value', 'list': [1, 2, 3]}")
    assert result == {"key": "value", "list": [1, 2, 3]}


def test_attempt_literal_eval_invalid():
    """Test literal_eval with invalid Python literal"""
    result = _attempt_literal_eval("import os")
    assert result is None


# Tests for parse_mcp_response
def test_parse_mcp_response_with_result():
    """Test parsing response with 'result' field"""
    response = {"result": {"content": [{"text": '["item1", "item2", "item3"]'}]}}
    result = parse_mcp_response(response)
    assert result == ["item1", "item2", "item3"]


def test_parse_mcp_response_without_result():
    """Test parsing response without 'result' field"""
    response = {"content": [{"text": '{"status": "success"}'}]}
    result = parse_mcp_response(response)
    assert result == {"status": "success"}


def test_parse_mcp_response_string_result():
    """Test parsing response where result is a string"""
    response = {"result": '{"data": [1, 2, 3]}'}
    result = parse_mcp_response(response)
    assert result == {"data": [1, 2, 3]}


def test_parse_mcp_response_plain_text():
    """Test parsing response with plain text content"""
    response = {"result": {"content": [{"text": "Plain text response"}]}}
    result = parse_mcp_response(response)
    assert result == "Plain text response"


def test_parse_mcp_response_python_literal():
    """Test parsing response with Python literal string"""
    response = {"result": {"content": [{"text": "{'python': 'dict', 'number': 42}"}]}}
    result = parse_mcp_response(response)
    assert result == {"python": "dict", "number": 42}


def test_parse_mcp_response_direct_dict():
    """Test parsing response that's already a dict"""
    response = {"result": {"data": "value", "number": 123}}
    result = parse_mcp_response(response)
    assert result == {"data": "value", "number": 123}


# Tests for _format_list_result
def test_format_list_result_strings():
    """Test formatting a list of strings"""
    items = ["apple", "banana", "cherry"]
    result = _format_list_result(items)
    assert result == "  - apple\n  - banana\n  - cherry"


def test_format_list_result_objects():
    """Test formatting a list of objects"""
    items = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    result = _format_list_result(items)
    parsed = json.loads(result)
    assert parsed == items


def test_format_list_result_empty():
    """Test formatting an empty list"""
    result = _format_list_result([])
    assert result == "No items returned."


def test_format_list_result_mixed():
    """Test formatting a list with mixed types"""
    items = ["string", 42, {"key": "value"}]
    result = _format_list_result(items)
    parsed = json.loads(result)
    assert parsed == items


# Tests for _format_tabular_data
def test_format_tabular_data_with_columns():
    """Test formatting tabular data with column names"""
    data = {
        "columns": ["id", "name", "age"],
        "rows": [[1, "Alice", 30], [2, "Bob", 25], [3, "Charlie", None]],
    }
    result = _format_tabular_data(data)
    assert "| id | name | age |" in result
    assert "|---|---|---|" in result
    assert "| 1 | Alice | 30 |" in result
    assert "| 3 | Charlie | NULL |" in result


def test_format_tabular_data_without_columns():
    """Test formatting tabular data without column names"""
    data = {"rows": [["value1", "value2"], ["value3", "value4"]]}
    result = _format_tabular_data(data)
    assert "| Col1 | Col2 |" in result
    assert "| value1 | value2 |" in result


def test_format_tabular_data_empty_rows():
    """Test formatting tabular data with no rows"""
    data = {"rows": [], "columns": ["col1", "col2"]}
    result = _format_tabular_data(data)
    assert result == "Query returned no results."


def test_format_tabular_data_non_list_rows():
    """Test formatting when rows are not lists"""
    data = {"rows": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
    result = _format_tabular_data(data)
    # Should fall back to JSON formatting
    parsed = json.loads(result)
    assert parsed == data["rows"]


# Tests for format_mcp_result
def test_format_mcp_result_none():
    """Test formatting None result"""
    result = format_mcp_result(None)
    assert result == "No data returned."


def test_format_mcp_result_list():
    """Test formatting list result"""
    data = ["item1", "item2"]
    result = format_mcp_result(data)
    assert "  - item1" in result
    assert "  - item2" in result


def test_format_mcp_result_dict_with_rows():
    """Test formatting dict with rows/columns structure"""
    data = {"columns": ["name", "value"], "rows": [["key1", "val1"], ["key2", "val2"]]}
    result = format_mcp_result(data)
    assert "| name | value |" in result
    assert "| key1 | val1 |" in result


def test_format_mcp_result_plain_dict():
    """Test formatting plain dictionary"""
    data = {"status": "success", "count": 42}
    result = format_mcp_result(data)
    parsed = json.loads(result)
    assert parsed == data


def test_format_mcp_result_string():
    """Test formatting string result"""
    data = "Simple string result"
    result = format_mcp_result(data)
    assert result == "Simple string result"


def test_format_mcp_result_number():
    """Test formatting numeric result"""
    data = 42
    result = format_mcp_result(data)
    assert result == "42"


# Integration tests
def test_parse_and_format_integration():
    """Test the full pipeline from parsing to formatting"""
    # Test with a typical MCP response structure
    raw_response = {
        "result": {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "columns": ["id", "name", "status"],
                            "rows": [
                                [1, "Task 1", "completed"],
                                [2, "Task 2", "pending"],
                                [3, "Task 3", "in_progress"],
                            ],
                        }
                    )
                }
            ]
        }
    }

    parsed = parse_mcp_response(raw_response)
    formatted = format_mcp_result(parsed)

    assert "| id | name | status |" in formatted
    assert "| 1 | Task 1 | completed |" in formatted
    assert "| 2 | Task 2 | pending |" in formatted
    assert "| 3 | Task 3 | in_progress |" in formatted


def test_parse_and_format_list_integration():
    """Test parsing and formatting a list response"""
    raw_response = {"result": '["file1.txt", "file2.py", "file3.js"]'}

    parsed = parse_mcp_response(raw_response)
    formatted = format_mcp_result(parsed)

    assert "  - file1.txt" in formatted
    assert "  - file2.py" in formatted
    assert "  - file3.js" in formatted
