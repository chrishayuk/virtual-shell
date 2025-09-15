"""
LLM interface for agent execution using chuk-llm.
"""

import asyncio
import json
import random
import logging
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)


class LLMInterface:
    """Interface for interacting with Large Language Models"""

    def __init__(self):
        """Initialize the LLM interface"""
        self.mock_mode = True  # Set to False when LLM is available
        self.client = None
        self.use_chuk_llm = False
        self.use_openai = False

        # Try to import chuk-llm first
        try:
            from chuk_llm import configure, ask, stream  # type: ignore

            self.chuk_ask = ask
            self.chuk_stream = stream
            self.chuk_configure = configure
            self.use_chuk_llm = True
            self.mock_mode = False
            logger.info("chuk-llm available, using chuk-llm interface")
        except (ImportError, AttributeError) as e:
            logger.warning(f"chuk-llm import failed: {e}")
            # Try to use OpenAI directly
            try:
                import openai
                import os

                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = openai.OpenAI(api_key=api_key)
                    self.use_openai = True
                    self.mock_mode = False
                    logger.info("OpenAI available, using direct OpenAI interface")
                else:
                    logger.info("OpenAI API key not found, using mock mode")
            except ImportError:
                logger.info("Neither chuk-llm nor openai available, using mock mode")

    async def generate(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable] = None,
    ) -> str:
        """Generate a response from the LLM"""

        if self.mock_mode:
            return await self._mock_generate(messages, tools, tool_executor)

        try:
            if self.use_chuk_llm:
                return await self._generate_with_chuk_llm(
                    model, messages, temperature, max_tokens, tools, tool_executor
                )
            elif self.use_openai:
                return await self._generate_with_openai(
                    model, messages, temperature, max_tokens, tools, tool_executor
                )
            else:
                return await self._mock_generate(messages, tools, tool_executor)
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"Error: {e}"

    async def _generate_with_chuk_llm(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        tools: Optional[List[Dict[str, Any]]],
        tool_executor: Optional[Callable],
    ) -> str:
        """Generate using chuk-llm"""
        # Configure chuk-llm with the specified model and parameters
        config = {"model": model, "temperature": temperature}
        if max_tokens:
            config["max_tokens"] = max_tokens

        self.chuk_configure(**config)

        # Convert from OpenAI format to a simple prompt
        prompt = self._format_messages(messages)

        # If tools are provided, add them to the prompt
        if tools and tool_executor:
            prompt = self._add_tools_to_prompt(prompt, tools)

        # Generate response using chuk-llm
        try:
            # chuk_ask might not be truly async, so wrap it
            if asyncio.iscoroutinefunction(self.chuk_ask):
                response = await self.chuk_ask(prompt)
            else:
                # Run in thread pool if it's blocking
                response = await asyncio.to_thread(self.chuk_ask, prompt)
        except Exception as api_error:
            # If API call fails, log and use mock
            logger.warning(f"API call failed: {api_error}, using mock response")
            return await self._mock_generate(messages, tools, tool_executor)

        # Process tool calls if any
        if tools and tool_executor and self._contains_tool_call(response):
            response = await self._process_tool_calls(response, tool_executor)

        return response

    async def _generate_with_openai(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        tools: Optional[List[Dict[str, Any]]],
        tool_executor: Optional[Callable],
    ) -> str:
        """Generate using OpenAI directly"""
        try:
            # Prepare OpenAI API call parameters
            params = {"model": model, "messages": messages, "temperature": temperature}
            if max_tokens:
                params["max_tokens"] = max_tokens

            # Add tools if provided
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"

            # Make API call
            response = await asyncio.to_thread(
                self.client.chat.completions.create, **params
            )

            # Extract response content
            message = response.choices[0].message

            # Handle tool calls if present
            if message.tool_calls and tool_executor:
                content = await self._process_openai_tool_calls(
                    message.tool_calls, tool_executor
                )
                if message.content:
                    content = message.content + "\n\n" + content
                return content

            return message.content or "No response generated"

        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}, falling back to mock mode")
            return await self._mock_generate(messages, tools, tool_executor)

    async def _mock_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable] = None,
    ) -> str:
        """Mock LLM generation for testing"""

        # Simulate some processing time
        await asyncio.sleep(0.1)

        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break

        # Generate mock responses based on patterns
        if not user_message:
            return "Hello! I'm an AI agent running in your shell. How can I help you?"

        # Check for specific patterns
        if "list" in user_message.lower() and "files" in user_message.lower():
            if tools and tool_executor:
                # Simulate using the ls tool
                result = tool_executor("ls", {"args": ""})
                return f"Here are the files in the current directory:\n{result}"
            return "I would list files here, but I don't have access to the ls command."

        elif "create" in user_message.lower() and "file" in user_message.lower():
            if tools and tool_executor:
                # Simulate creating a file
                result = tool_executor("touch", {"args": "example.txt"})
                return f"I've created a file called example.txt\n{result}"
            return "I would create a file, but I don't have access to file commands."

        elif "hello" in user_message.lower():
            responses = [
                "Hello! How can I assist you today?",
                "Hi there! I'm ready to help with your tasks.",
                "Greetings! What would you like me to do?",
            ]
            return random.choice(responses)

        elif "help" in user_message.lower():
            return (
                "I'm an AI agent that can:\n"
                "- Execute shell commands\n"
                "- Process and analyze text\n"
                "- Help with various tasks\n"
                "Try asking me to list files, create files, or analyze data!"
            )

        elif "analyze" in user_message.lower():
            return (
                f"Analyzing input: '{user_message}'\n"
                f"- Length: {len(user_message)} characters\n"
                f"- Words: {len(user_message.split())} words\n"
                f"- Contains question: {'?' in user_message}\n"
                "Analysis complete."
            )

        else:
            # Generic response
            return f"I understand you said: '{user_message}'. As a mock agent, I have limited capabilities. In a real implementation, I would process this request more intelligently."

    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages list into a single prompt"""
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(content)

        return "\n\n".join(prompt_parts)

    def _add_tools_to_prompt(self, prompt: str, tools: List[Dict[str, Any]]) -> str:
        """Add available tools to the prompt"""
        tool_desc = "\n\nAvailable tools:\n"
        for tool in tools:
            tool_desc += (
                f"- {tool['name']}: {tool.get('description', 'No description')}\n"
            )

        tool_desc += "\nYou can use tools by writing: TOOL[tool_name](arguments)\n"

        return prompt + tool_desc

    def _contains_tool_call(self, response: str) -> bool:
        """Check if response contains tool calls"""
        return "TOOL[" in response

    async def _process_openai_tool_calls(
        self, tool_calls, tool_executor: Callable
    ) -> str:
        """Process OpenAI tool calls"""
        results = []

        for tool_call in tool_calls:
            try:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute the tool
                result = await tool_executor(function_name, function_args)
                results.append(f"Tool {function_name}: {result}")

            except Exception as e:
                results.append(f"Tool {tool_call.function.name} error: {e}")

        return "\n".join(results)

    async def _process_tool_calls(self, response: str, tool_executor: Callable) -> str:
        """Process tool calls in the response"""
        import re

        # Find all tool calls in format: TOOL[name](args) or TOOL[name]
        pattern_with_args = r"TOOL\[([^\]]+)\]\(([^\)]*)\)"
        pattern_without_args = r"TOOL\[([^\]]+)\](?!\()"

        # Process tool calls with arguments first
        matches = re.findall(pattern_with_args, response)
        for tool_name, args in matches:
            try:
                result = tool_executor(tool_name, {"args": args})
                tool_call = f"TOOL[{tool_name}]({args})"
                response = response.replace(
                    tool_call, f"[{tool_name} result: {result}]"
                )
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                response = response.replace(
                    tool_call, f"[Error executing {tool_name}: {e}]"
                )

        # Process tool calls without arguments
        matches = re.findall(pattern_without_args, response)
        for tool_name in matches:
            try:
                # Execute the tool
                result = tool_executor(tool_name, {"args": ""})
                # Replace the tool call with the result
                tool_call = f"TOOL[{tool_name}]"
                response = response.replace(
                    tool_call, f"[{tool_name} result: {result}]"
                )
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                response = response.replace(
                    f"TOOL[{tool_name}]", f"[Error executing {tool_name}: {e}]"
                )

        return response

    def set_provider(self, provider: str, **config):
        """Configure a specific LLM provider"""
        if not self.mock_mode:
            try:
                self.chuk_configure(provider=provider, **config)
            except Exception as e:
                logger.error(f"Error configuring provider: {e}")
        else:
            logger.warning("Cannot set provider in mock mode")
