"""Puter AI client module for interacting with Puter.js AI models."""

import asyncio
import base64
import copy
import json
import mimetypes
import os
import time
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Sequence, Tuple, Union
from urllib.parse import urlparse

import aiohttp
import requests
from asyncio_throttle import Throttler

from .config import config
from .exceptions import PuterAPIError, PuterAuthError

ImageInputType = Union[
    str,
    os.PathLike,
    bytes,
    IO[bytes],
    Dict[str, Any],
    Tuple[Union[str, os.PathLike, bytes, IO[bytes]], Optional[str]],
]


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
        self.chat_history: List[Dict[str, Any]] = []
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

    def _prepare_image_content(
        self,
        image: ImageInputType,
        *,
        default_mime: str = "image/png",
    ) -> Dict[str, Any]:
        """Convert various image inputs into the API-compatible payload."""
        source, explicit_mime = self._extract_image_source(image)

        if isinstance(source, dict):
            return copy.deepcopy(source)

        if isinstance(source, (str, os.PathLike)):
            return self._handle_path_like_image(source, explicit_mime, default_mime)

        data, mime_type = self._extract_image_data(source, explicit_mime, default_mime)
        return self._create_base64_image_url(data, mime_type, default_mime)

    def _extract_image_source(self, image: ImageInputType) -> tuple:
        """Extract source and explicit mime type from image input."""
        if isinstance(image, tuple):
            if len(image) != 2:
                raise ValueError("Tuple image inputs must be (image_data, mime_type).")
            return image
        return image, None

    def _handle_path_like_image(
        self, source, explicit_mime: Optional[str], default_mime: str
    ) -> Dict[str, Any]:
        """Handle path-like image inputs (strings and PathLike objects)."""
        path_str = str(source)

        if path_str.startswith("data:"):
            return {"type": "image_url", "image_url": {"url": path_str}}

        parsed = urlparse(path_str)
        if parsed.scheme in {"http", "https"}:
            return {"type": "image_url", "image_url": {"url": path_str}}

        return self._handle_file_path(path_str, explicit_mime, default_mime)

    def _handle_file_path(
        self, path_str: str, explicit_mime: Optional[str], default_mime: str
    ) -> Dict[str, Any]:
        """Handle local file path images."""
        file_path = Path(path_str)
        if not file_path.exists():
            raise ValueError(f"Image file not found: {path_str}")

        data = file_path.read_bytes()
        mime_type = explicit_mime or mimetypes.guess_type(path_str)[0] or default_mime
        return self._create_base64_image_url(data, mime_type, default_mime)

    def _extract_image_data(
        self, source, explicit_mime: Optional[str], default_mime: str
    ) -> tuple:
        """Extract image data and mime type from various source types."""
        if isinstance(source, bytes):
            return source, explicit_mime or default_mime

        if hasattr(source, "read") and not isinstance(
            source, (str, bytes, os.PathLike, tuple)
        ):
            file_obj = source  # type: IO[bytes]
            raw = file_obj.read()
            if isinstance(raw, str):
                data = raw.encode("utf-8")
            else:
                data = raw
            mime_type = (
                explicit_mime or getattr(source, "mimetype", None) or default_mime
            )
            return data, mime_type

        raise ValueError(
            "Unsupported image input type. Provide a path, bytes, file-like "
            "object, data URL, HTTP(S) URL, or a pre-built image payload."
        )

    def _create_base64_image_url(
        self, data, mime_type: str, default_mime: str
    ) -> Dict[str, Any]:
        """Create a base64 encoded image URL payload."""
        if data is None:
            raise ValueError("Image data could not be read.")

        if not isinstance(data, (bytes, bytearray)):
            raise ValueError("Image data must be bytes-like.")

        encoded = base64.b64encode(bytes(data)).decode("utf-8")
        mime = mime_type or default_mime

        return {
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{encoded}"},
        }

    def _build_user_content(
        self,
        prompt: Optional[str],
        images: Optional[Sequence[ImageInputType]],
        content_parts: Optional[Sequence[Dict[str, Any]]],
    ) -> Union[str, List[Dict[str, Any]]]:
        """Construct the content payload for a user message."""
        if content_parts is not None:
            return self._handle_custom_content_parts(content_parts)

        parts = self._build_content_parts(prompt, images)
        return self._optimize_content_parts(parts)

    def _handle_custom_content_parts(
        self, content_parts: Sequence[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Handle custom content parts input."""
        if not content_parts:
            raise ValueError("content_parts cannot be empty.")
        return [copy.deepcopy(part) for part in content_parts]

    def _build_content_parts(
        self, prompt: Optional[str], images: Optional[Sequence[ImageInputType]]
    ) -> List[Dict[str, Any]]:
        """Build content parts from prompt and images."""
        parts: List[Dict[str, Any]] = []

        if prompt:
            parts.append({"type": "text", "text": str(prompt)})

        if images:
            for image in images:
                parts.append(self._prepare_image_content(image))

        if not parts:
            raise ValueError(
                "Provide at least a prompt, content_parts, or images when "
                "sending a message."
            )

        return parts

    def _optimize_content_parts(
        self, parts: List[Dict[str, Any]]
    ) -> Union[str, List[Dict[str, Any]]]:
        """Optimize content parts - return string if only single text part."""
        if len(parts) == 1 and parts[0].get("type") == "text":
            return parts[0]["text"]
        return parts

    def _build_user_message(
        self,
        prompt: Optional[str],
        images: Optional[Sequence[ImageInputType]],
        content_parts: Optional[Sequence[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Create the user message dictionary for the API payload."""
        content = self._build_user_content(prompt, images, content_parts)
        return {"role": "user", "content": content}

    def chat(
        self,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        *,
        images: Optional[Sequence[ImageInputType]] = None,
        content_parts: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> str:
        """Send a chat message to the AI model and return its response.

        The conversation history is automatically managed.

        Args:
            prompt (Optional[str]): The user's message. May be omitted when
                using ``content_parts`` or ``images``.
            model (Optional[str]): The model to use for this specific chat.
                Defaults to current_model.
            images (Optional[Sequence[ImageInputType]]): Optional collection of
                images to send with the message. Items can be file paths,
                bytes, file-like objects, HTTP(S)/data URLs, tuples of
                (data, mime_type), or pre-built image payload dictionaries.
            content_parts (Optional[Sequence[Dict[str, Any]]]): Provide the
                exact message content structure when you need fine-grained
                control (e.g., custom multimodal payloads). When supplied,
                ``prompt`` and ``images`` are ignored.

        Raises:
            ValueError: If no prompt/content/images are supplied or an image
                input is invalid.
            PuterAPIError: If the API call fails.

        Returns:
            str: The AI's response as a string.
        """
        if model is None:
            model = self.current_model

        user_message = self._build_user_message(prompt, images, content_parts)
        messages = [*self.chat_history, user_message]
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
                self.chat_history.append(copy.deepcopy(user_message))
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

    async def async_chat(
        self,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        *,
        images: Optional[Sequence[ImageInputType]] = None,
        content_parts: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> str:
        """Send a chat message to the AI model and return its response (async).

        The conversation history is automatically managed.

        Args:
            prompt (Optional[str]): The user's message. May be omitted when
                using ``content_parts`` or ``images``.
            model (Optional[str]): The model to use for this specific chat.
                Defaults to current_model.
            images (Optional[Sequence[ImageInputType]]): Optional collection of
                images to send with the message (see ``chat`` for details).
            content_parts (Optional[Sequence[Dict[str, Any]]]): Custom content
                payload overriding ``prompt`` and ``images`` when provided.

        Raises:
            ValueError: If no prompt/content/images are supplied or an image
                input is invalid.
            PuterAPIError: If the API call fails.

        Returns:
            str: The AI's response as a string.
        """
        if model is None:
            model = self.current_model

        user_message = self._build_user_message(prompt, images, content_parts)
        messages = [*self.chat_history, user_message]
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
                self.chat_history.append(copy.deepcopy(user_message))
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
