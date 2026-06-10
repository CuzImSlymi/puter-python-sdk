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
    """Client for interacting with Puter.js AI models."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        **config_overrides,
    ):
        self._token = token
        self._username = username
        self._password = password
        self.chat_history: List[Dict[str, Any]] = []
        self.current_model = "claude-opus-4"

        if config_overrides:
            config.update(**config_overrides)

        self._throttler = Throttler(
            rate_limit=config.rate_limit_requests,
            period=config.rate_limit_period,
        )

        # Retrieve available models from the Puter API
        try:
            response = requests.get(
                "https://api.puter.com/puterai/chat/models",
                headers=config.headers,
                timeout=5
            )
            response.raise_for_status()
            self.available_models = response.json().get("models", [])
        except Exception:
            # Fallback list of models if offline or network request fails
            self.available_models = [
                "anthropic:anthropic/claude-opus-4",
                "anthropic:anthropic/claude-fable-5",
                "anthropic:anthropic/claude-opus-4-8",
                "openrouter:anthropic/claude-opus-4.8-fast",
                "anthropic:anthropic/claude-3-5-sonnet",
                "anthropic:anthropic/claude-3-5-sonnet-latest"
            ]

    def _retry_request(self, request_func, *args, **kwargs):
        """Execute request with retry logic and exponential backoff."""
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
            f"Request failed after {config.max_retries + 1} attempts: {last_exception}"
        )

    async def _async_retry_request(
        self, session: aiohttp.ClientSession, method: str, url: str, **kwargs
    ):
        """Execute async request with retry logic and exponential backoff."""
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
            f"Async request failed after {config.max_retries + 1} attempts: {last_exception}"
        )

    def login(self) -> bool:
        """Authenticate with Puter.js using username and password."""
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
            raise PuterAuthError("Login failed. Please check your credentials.")
        except Exception as e:
            raise PuterAuthError(f"Login error: {e}")

    async def async_login(self) -> bool:
        """Async login version."""
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
                    raise PuterAuthError("Login failed. Please check your credentials.")
        except Exception as e:
            raise PuterAuthError(f"Async login error: {e}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get auth headers required by the new drivers/call endpoint."""
        if not self._token:
            raise PuterAuthError("Not authenticated. Please login first.")
        headers = {
            **config.headers,
            "Content-Type": "text/plain;actually=json",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _get_driver_for_model(self, model_name: str) -> str:
        """Unified 'ai-chat' driver is used for all models now."""
        return "ai-chat"

    def _resolve_model(self, model_name: str) -> str:
        """Resolve short model names (e.g. claude-fable-5) to full names from API."""
        if model_name in self.available_models:
            return model_name
        for model in self.available_models:
            parts = model.split(":")
            if len(parts) > 1:
                name_parts = parts[-1].split("/")
                if name_parts[-1].lower() == model_name.lower():
                    return model
        for model in self.available_models:
            if model.lower().endswith(model_name.lower()):
                return model
        return model_name

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
        if isinstance(image, tuple):
            if len(image) != 2:
                raise ValueError("Tuple image inputs must be (image_data, mime_type).")
            return image
        return image, None

    def _handle_path_like_image(
        self, source, explicit_mime: Optional[str], default_mime: str
    ) -> Dict[str, Any]:
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
        file_path = Path(path_str)
        if not file_path.exists():
            raise ValueError(f"Image file not found: {path_str}")

        data = file_path.read_bytes()
        mime_type = explicit_mime or mimetypes.guess_type(path_str)[0] or default_mime
        return self._create_base64_image_url(data, mime_type, default_mime)

    def _extract_image_data(
        self, source, explicit_mime: Optional[str], default_mime: str
    ) -> tuple:
        if isinstance(source, bytes):
            return source, explicit_mime or default_mime

        if hasattr(source, "read") and not isinstance(
            source, (str, bytes, os.PathLike, tuple)
        ):
            file_obj = source
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
        if content_parts is not None:
            return self._handle_custom_content_parts(content_parts)

        parts = self._build_content_parts(prompt, images)
        return self._optimize_content_parts(parts)

    def _handle_custom_content_parts(
        self, content_parts: Sequence[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not content_parts:
            raise ValueError("content_parts cannot be empty.")
        return [copy.deepcopy(part) for part in content_parts]

    def _build_content_parts(
        self, prompt: Optional[str], images: Optional[Sequence[ImageInputType]]
    ) -> List[Dict[str, Any]]:
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
        if len(parts) == 1 and parts[0].get("type") == "text":
            return parts[0]["text"]
        return parts

    def _build_user_message(
        self,
        prompt: Optional[str],
        images: Optional[Sequence[ImageInputType]],
        content_parts: Optional[Sequence[Dict[str, Any]]],
    ) -> Dict[str, Any]:
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
        """Send a chat message to the AI model and return its response."""
        if model is None:
            model = self.current_model

        resolved_model = self._resolve_model(model)
        user_message = self._build_user_message(prompt, images, content_parts)
        messages = [*self.chat_history, user_message]

        args = {
            "messages": messages,
            "model": resolved_model,
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

        payload = {
            "interface": "puter-chat-completion",
            "driver": "ai-chat",
            "method": "complete",
            "args": args,
            "stream": False,
            "testMode": False,
            "auth_token": self._token
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

            def extract_content(data):
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
        """Send a chat message to the AI model and return its response (async)."""
        if model is None:
            model = self.current_model

        resolved_model = self._resolve_model(model)
        user_message = self._build_user_message(prompt, images, content_parts)
        messages = [*self.chat_history, user_message]

        args = {
            "messages": messages,
            "model": resolved_model,
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

        payload = {
            "interface": "puter-chat-completion",
            "driver": "ai-chat",
            "method": "complete",
            "args": args,
            "stream": False,
            "testMode": False,
            "auth_token": self._token
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

            def extract_content(data):
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
        """Set the current AI model for subsequent chat interactions."""
        resolved = self._resolve_model(model_name)
        if resolved in self.available_models:
            self.current_model = resolved
            return True
        return False

    def get_available_models(self) -> List[str]:
        """Retrieve a list of all available AI model names."""
        return self.available_models
