# src/chuk_virtual_shell/commands/mcp/mcp_output_formatter.py
"""
chuk_virtual_shell/commands/mcp/mcp_output_formatter.py
"""

import json
import ast
import logging

# logger
logger = logging.getLogger(__name__)


def parse_mcp_response(raw_response):
    """
    Parse the top-level response from the MCP server, which may contain
    either a `result` key or direct `content`. Returns a Python object
    (list, dict, or string) that represents the parsed data.
    """
    logger.debug(f"Raw response received: {raw_response}")

    # 1) Determine which dict actually holds the data
    #    If `result` is missing or empty, fallback to raw_response itself.
    result_section = raw_response.get("result")
    if not result_section:
        logger.debug(
            "No 'result' field found; using raw_response as the result section."
        )
        result_section = raw_response

    logger.debug(f"Using result section: {result_section}")

    # 2) Check for 'content' at whichever level we end up with.
    if isinstance(result_section, dict) and "content" in result_section:
        content_list = result_section["content"]
        if content_list and isinstance(content_list, list):
            first_item = content_list[0]
            if isinstance(first_item, dict) and "text" in first_item:
                raw_text = first_item["text"]
                logger.debug(f"Extracted text from 'content': {raw_text}")
                # Attempt JSON first
                parsed_obj = _attempt_json_load(raw_text)
                if parsed_obj is None:
                    # Then fall back to ast.literal_eval
                    parsed_obj = _attempt_literal_eval(raw_text)
                return parsed_obj if parsed_obj is not None else raw_text

    # 3) If the result_section is still a string, try to parse it
    if isinstance(result_section, str):
        parsed_obj = _attempt_json_load(result_section)
        if parsed_obj is None:
            parsed_obj = _attempt_literal_eval(result_section)
        return parsed_obj if parsed_obj is not None else result_section

    # Not a string; return as-is
    return result_section


def _attempt_json_load(raw_text):
    """Try to parse raw_text as JSON, return None if it fails."""
    try:
        return json.loads(raw_text)
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def _attempt_literal_eval(raw_text):
    """Try to parse raw_text with ast.literal_eval, return None if it fails."""
    try:
        return ast.literal_eval(raw_text)
    except Exception:
        return None


def format_mcp_result(data):
    """
    Format the parsed data from parse_mcp_response into a user-friendly
    string (JSON, table, list, etc.).
    """
    if data is None:
        return "No data returned."

    # 1) List
    if isinstance(data, list):
        return _format_list_result(data)

    # 2) Dict (check for rows/columns)
    if isinstance(data, dict):
        if "rows" in data and isinstance(data["rows"], list):
            return _format_tabular_data(data)
        return json.dumps(data, indent=2, sort_keys=True)

    # 3) Fallback
    return str(data)


def _format_list_result(items):
    """Format a list of items as either plain lines or pretty JSON if it contains objects."""
    if not items:
        return "No items returned."
    # If all items are strings, display them line by line
    if all(isinstance(i, str) for i in items):
        return "\n".join(f"  - {i}" for i in items)
    # Otherwise, display as JSON
    return json.dumps(items, indent=2)


def _format_tabular_data(data):
    """If data has rows/columns, display in a markdown table; otherwise show as JSON list."""
    rows = data.get("rows", [])
    if not rows:
        return "Query returned no results."

    columns = data.get("columns", [])
    # If columns are missing but rows exist, assume numeric columns
    if not columns and rows and isinstance(rows[0], list):
        columns = [f"Col{i + 1}" for i in range(len(rows[0]))]

    if columns:
        # Create a markdown table
        header = "| " + " | ".join(str(c) for c in columns) + " |\n"
        separator = "|" + "---|" * len(columns) + "\n"
        rows_str = ""
        for row in rows:
            row_values = [str(cell) if cell is not None else "NULL" for cell in row]
            rows_str += "| " + " | ".join(row_values) + " |\n"
        return header + separator + rows_str

    # Fallback to JSON if no recognized pattern
    return json.dumps(rows, indent=2)
