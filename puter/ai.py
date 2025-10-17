"""Puter AI client module for interacting with Puter.js AI models."""

import asyncio
import json
import os
import time
from typing import Dict, List, Optional

import aiohttp
import requests
from asyncio_throttle import Throttler

from .config import config
from .exceptions import PuterAPIError, PuterAuthError


class PuterAI:
    """Client for interacting with Puter.js AI models.

    This class handles authentication, model selection, and chat interactions
    with the Puter.js AI API with enhanced features like retry logic, rate
    limiting, and async support.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        **config_overrides,
    ):
        """Initialize the PuterAI client.

        Args:
            username (Optional[str]): Your Puter.js username.
            password (Optional[str]): Your Puter.js password.
            token (Optional[str]): An existing authentication token. If
                provided, username and password are not needed.
            **config_overrides: Override default configuration values.
        """
        self._token = token
        self._username = username
        self._password = password
        self.chat_history: List[Dict[str, str]] = []
        self.current_model = "claude-opus-4"  # default model

        # Apply configuration overrides
        if config_overrides:
            config.update(**config_overrides)

        # Rate limiting setup
        self._throttler = Throttler(
            rate_limit=config.rate_limit_requests,
            period=config.rate_limit_period,
        )

        # Get the path to the available_models.json file relative to module
        current_dir = os.path.dirname(__file__)
        models_file = os.path.join(current_dir, "available_models.json")
        with open(models_file) as f:
            self.available_models = json.load(f)

    def _retry_request(self, request_func, *args, **kwargs):
        """Execute a request with retry logic and exponential backoff.

        Args:
            request_func: The function to execute (requests.post, etc.)
            *args, **kwargs: Arguments to pass to the request function

        Returns:
            The response from the request

        Raises:
            PuterAPIError: If all retries are exhausted
        """
        last_exception = None

        for attempt in range(config.max_retries + 1):
            try:
                if "timeout" not in kwargs:
                    kwargs["timeout"] = config.timeout

                response = request_func(*args, **kwargs)
                response.raise_for_status()
                return response

            except Exception as e:
                last_exception = e
                if attempt < config.max_retries:
                    delay = config.retry_delay * (config.backoff_factor**attempt)
                    time.sleep(delay)
                    continue
                break

        raise PuterAPIError(
            f"Request failed after {config.max_retries + 1} attempts: "
            f"{last_exception}"
        )

    async def _async_retry_request(
        self, session: aiohttp.ClientSession, method: str, url: str, **kwargs
    ):
        """Execute an async request with retry logic and exponential backoff.

        Args:
            session: The aiohttp session
            method: HTTP method (GET, POST, etc.)
            url: The URL to request
            **kwargs: Additional arguments for the request

        Returns:
            The response from the request

        Raises:
            PuterAPIError: If all retries are exhausted
        """
        last_exception = None

        for attempt in range(config.max_retries + 1):
            try:
                if "timeout" not in kwargs:
                    timeout = aiohttp.ClientTimeout(total=config.timeout)
                    kwargs["timeout"] = timeout

                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()

            except Exception as e:
                last_exception = e
                if attempt < config.max_retries:
                    delay = config.retry_delay * (config.backoff_factor**attempt)
                    await asyncio.sleep(delay)
                    continue
                break

        raise PuterAPIError(
            f"Async request failed after {config.max_retries + 1} attempts: "
            f"{last_exception}"
        )

    def login(self) -> bool:
        """Authenticate with Puter.js using the provided username and password.

        Raises:
            PuterAuthError: If username or password are not set, or if
                login fails.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        if not self._username or not self._password:
            raise PuterAuthError("Username and password must be set for login.")

        payload = {"username": self._username, "password": self._password}
        try:
            response = self._retry_request(
                requests.post,
                config.login_url,
                headers=config.headers,
                json=payload,
            )
            data = response.json()
            if data.get("proceed"):
                self._token = data["token"]
                return True
            else:
                raise PuterAuthError("Login failed. Please check your credentials.")
        except Exception as e:
            raise PuterAuthError(f"Login error: {e}")

    async def async_login(self) -> bool:
        """Async version of login method.

        Raises:
            PuterAuthError: If username or password are not set, or if
                login fails.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        if not self._username or not self._password:
            raise PuterAuthError("Username and password must be set for login.")

        payload = {"username": self._username, "password": self._password}
        try:
            async with self._throttler:
                async with aiohttp.ClientSession() as session:
                    data = await self._async_retry_request(
                        session,
                        "POST",
                        config.login_url,
                        headers=config.headers,
                        json=payload,
                    )
                    if data.get("proceed"):
                        self._token = data["token"]
                        return True
                    else:
                        raise PuterAuthError(
                            "Login failed. Please check your credentials."
                        )
        except Exception as e:
            raise PuterAuthError(f"Async login error: {e}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get the authorization headers for API requests.

        Raises:
            PuterAuthError: If not authenticated.

        Returns:
            Dict[str, str]: A dictionary of headers including the authorization
                token.
        """
        if not self._token:
            raise PuterAuthError("Not authenticated. Please login first.")
        return {
            **config.headers,
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _get_driver_for_model(self, model_name: str) -> str:
        """Determine the backend driver for a given model name.

        Args:
            model_name (str): The name of the AI model.

        Returns:
            str: The corresponding driver name (e.g., "claude",
                "openai-completion").
        """
        return self.available_models.get(model_name, "openai-completion")

    def chat(self, prompt: str, model: Optional[str] = None) -> str:
        """Send a chat message to the AI model and return its response.

        The conversation history is automatically managed.

        Args:
            prompt (str): The user's message.
            model (Optional[str]): The model to use for this specific chat.
                Defaults to current_model.

        Raises:
            PuterAPIError: If the API call fails.

        Returns:
            str: The AI's response as a string.
        """
        if model is None:
            model = self.current_model

        messages = self.chat_history + [{"role": "user", "content": prompt}]
        driver = self._get_driver_for_model(model)

        args = {
            "messages": messages,
            "model": model,
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

        payload = {
            "interface": "puter-chat-completion",
            "driver": driver,
            "method": "complete",
            "args": args,
            "stream": False,
            "testMode": False,
        }

        headers = self._get_auth_headers()
        try:
            response = self._retry_request(
                requests.post,
                f"{config.api_base}/drivers/call",
                json=payload,
                headers=headers,
                stream=False,
            )
            response_data = response.json()

            # More robust response parsing with detailed debugging
            def extract_content(data):
                """Extract content from various possible response formats."""
                # Check if data has a result field
                if isinstance(data, dict) and "result" in data:
                    result = data["result"]

                    # Case 1: result.message.content (original expected format)
                    if isinstance(result, dict) and "message" in result:
                        message = result["message"]
                        if isinstance(message, dict) and "content" in message:
                            content = message["content"]
                            if isinstance(content, list):
                                return "".join(
                                    [
                                        item.get("text", "")
                                        for item in content
                                        if item.get("type") == "text"
                                    ]
                                )
                            elif isinstance(content, str):
                                return content

                    # Case 2: result.content (direct content in result)
                    if isinstance(result, dict) and "content" in result:
                        content = result["content"]
                        if isinstance(content, list):
                            return "".join(
                                [
                                    item.get("text", "")
                                    for item in content
                                    if item.get("type") == "text"
                                ]
                            )
                        elif isinstance(content, str):
                            return content

                    # Case 3: result is directly the content string
                    if isinstance(result, str):
                        return result

                    # Case 4: result.choices[0].message.content (OpenAI-style)
                    if isinstance(result, dict) and "choices" in result:
                        choices = result["choices"]
                        if isinstance(choices, list) and len(choices) > 0:
                            choice = choices[0]
                            if isinstance(choice, dict) and "message" in choice:
                                message = choice["message"]
                                if isinstance(message, dict) and "content" in message:
                                    return message["content"]

                    # Case 5: result.text (simple text field)
                    if isinstance(result, dict) and "text" in result:
                        return result["text"]

                # Case 6: Direct content field in root
                if isinstance(data, dict) and "content" in data:
                    content = data["content"]
                    if isinstance(content, str):
                        return content

                # Case 7: Direct text field in root
                if isinstance(data, dict) and "text" in data:
                    return data["text"]

                return None

            content = extract_content(response_data)

            if content and content.strip():
                self.chat_history.append({"role": "user", "content": prompt})
                self.chat_history.append({"role": "assistant", "content": content})
                return content
            else:
                # Enhanced debugging information
                import json

                debug_info = {
                    "status": response.status_code,
                    "response_keys": (
                        list(response_data.keys())
                        if isinstance(response_data, dict)
                        else "Not a dict"
                    ),
                    "response_preview": (
                        str(response_data)[:200] + "..."
                        if len(str(response_data)) > 200
                        else str(response_data)
                    ),
                }
                debug_str = json.dumps(debug_info, indent=2)
                return f"No content in AI response. Debug: {debug_str}"
        except Exception as e:
            raise PuterAPIError(f"AI chat error: {e}")

    async def async_chat(self, prompt: str, model: Optional[str] = None) -> str:
        """Send a chat message to the AI model and return its response (async).

        The conversation history is automatically managed.

        Args:
            prompt (str): The user's message.
            model (Optional[str]): The model to use for this specific chat.
                Defaults to current_model.

        Raises:
            PuterAPIError: If the API call fails.

        Returns:
            str: The AI's response as a string.
        """
        if model is None:
            model = self.current_model

        messages = self.chat_history + [{"role": "user", "content": prompt}]
        driver = self._get_driver_for_model(model)

        args = {
            "messages": messages,
            "model": model,
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

        payload = {
            "interface": "puter-chat-completion",
            "driver": driver,
            "method": "complete",
            "args": args,
            "stream": False,
            "testMode": False,
        }

        headers = self._get_auth_headers()
        try:
            async with self._throttler:
                async with aiohttp.ClientSession() as session:
                    response_data = await self._async_retry_request(
                        session,
                        "POST",
                        f"{config.api_base}/drivers/call",
                        json=payload,
                        headers=headers,
                    )

            # Use the same content extraction logic
            def extract_content(data):
                """Extract content from various possible response formats."""
                # [Same extraction logic as sync version]
                if isinstance(data, dict) and "result" in data:
                    result = data["result"]

                    if isinstance(result, dict) and "message" in result:
                        message = result["message"]
                        if isinstance(message, dict) and "content" in message:
                            content = message["content"]
                            if isinstance(content, list):
                                return "".join(
                                    [
                                        item.get("text", "")
                                        for item in content
                                        if item.get("type") == "text"
                                    ]
                                )
                            elif isinstance(content, str):
                                return content

                    if isinstance(result, dict) and "content" in result:
                        content = result["content"]
                        if isinstance(content, list):
                            return "".join(
                                [
                                    item.get("text", "")
                                    for item in content
                                    if item.get("type") == "text"
                                ]
                            )
                        elif isinstance(content, str):
                            return content

                    if isinstance(result, str):
                        return result

                    if isinstance(result, dict) and "choices" in result:
                        choices = result["choices"]
                        if isinstance(choices, list) and len(choices) > 0:
                            choice = choices[0]
                            if isinstance(choice, dict) and "message" in choice:
                                message = choice["message"]
                                if isinstance(message, dict) and "content" in message:
                                    return message["content"]

                    if isinstance(result, dict) and "text" in result:
                        return result["text"]

                if isinstance(data, dict) and "content" in data:
                    content = data["content"]
                    if isinstance(content, str):
                        return content

                if isinstance(data, dict) and "text" in data:
                    return data["text"]

                return None

            content = extract_content(response_data)

            if content and content.strip():
                self.chat_history.append({"role": "user", "content": prompt})
                self.chat_history.append({"role": "assistant", "content": content})
                return content
            else:
                debug_info = {
                    "response_keys": (
                        list(response_data.keys())
                        if isinstance(response_data, dict)
                        else "Not a dict"
                    ),
                    "response_preview": (
                        str(response_data)[:200] + "..."
                        if len(str(response_data)) > 200
                        else str(response_data)
                    ),
                }
                debug_str = json.dumps(debug_info, indent=2)
                return f"No content in AI response. Debug: {debug_str}"
        except Exception as e:
            raise PuterAPIError(f"Async AI chat error: {e}")

    def clear_chat_history(self):
        """Clear the current chat history."""
        self.chat_history = []

    def set_model(self, model_name: str) -> bool:
        """Set the current AI model for subsequent chat interactions.

        Args:
            model_name (str): The name of the model to set.

        Returns:
            bool: True if the model was successfully set, False otherwise.
        """
        if model_name in self.available_models:
            self.current_model = model_name
            return True
        return False

    def get_available_models(self) -> List[str]:
        """Retrieve a list of all available AI model names.

        Returns:
            List[str]: A list of strings, where each string is an available
                model name.
        """
        return list(self.available_models.keys())
