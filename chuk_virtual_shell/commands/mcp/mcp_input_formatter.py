# src/chuk_virtual_shell/commands/mcp/mcp_input_formatter.py
"""
chuk_virtual_shell/commands/mcp/mcp_input_formatter.py

This module handles formatting of user input for MCP tools based on the tool schema.
It converts a list of arguments into a dictionary payload that matches the expected input format.
"""

import logging

logger = logging.getLogger(__name__)


def format_mcp_input(args, tool_schema):
    """
    Format the user-provided arguments based on the given tool schema.

    Args:
        args (list): List of arguments provided by the user.
        tool_schema (dict): The input schema for the MCP tool.

    Returns:
        dict: A dictionary representing the formatted input data.
    """
    logger.debug(f"Formatting input with args: {args} and tool_schema: {tool_schema}")

    # If no tool_schema is provided, simply return the arguments under 'args'
    if not tool_schema:
        logger.debug("No tool_schema provided, returning args as 'args'.")
        return {"args": args}

    properties = tool_schema.get("properties", {})
    required = tool_schema.get("required", [])

    # If there are no properties in the schema, assume no input is needed
    if not properties:
        logger.debug("No properties defined in tool_schema, returning empty dict.")
        return {}

    # If there's exactly one required property and there are arguments,
    # use that property. Special-case for 'query': join all args into one string.
    if len(required) == 1 and len(args) > 0:
        prop_name = required[0]
        if prop_name == "query":
            formatted = {prop_name: " ".join(args)}
            logger.debug(
                f"Single required property 'query' detected. Formatted input: {formatted}"
            )
            return formatted
        formatted = {prop_name: args[0]}
        logger.debug(f"Single required property detected. Formatted input: {formatted}")
        return formatted

    # If there's a property named 'query' in the schema, join all arguments into a query string.
    if "query" in properties and args:
        formatted = {"query": " ".join(args)}
        logger.debug(
            f"'query' property detected in schema. Formatted input: {formatted}"
        )
        return formatted

    # Otherwise, return the arguments as is, under the key 'args'.
    formatted = {"args": args}
    logger.debug(f"Default input formatting applied. Formatted input: {formatted}")
    return formatted
