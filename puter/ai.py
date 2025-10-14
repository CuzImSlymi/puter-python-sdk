import json
import os
import requests
from typing import Any, Dict, List, Optional

from .exceptions import PuterAuthError, PuterAPIError

class PuterAI:
    """
    Client for interacting with Puter.js AI models.

    This class handles authentication, model selection, and chat interactions
    with the Puter.js AI API.
    """
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, token: Optional[str] = None):
        """
        Initializes the PuterAI client.

        Args:
            username (Optional[str]): Your Puter.js username.
            password (Optional[str]): Your Puter.js password.
            token (Optional[str]): An existing authentication token. If provided, username and password are not needed.
        """
        self._token = token
        self._api_base = "https://api.puter.com"
        self._login_url = "https://puter.com/login"
        self._headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://puter.com",
            "Referer": "https://puter.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        self._username = username
        self._password = password
        self.chat_history = []
        self.current_model = "claude-opus-4" # default model
        
        # Get the path to the available_models.json file relative to this module
        current_dir = os.path.dirname(__file__)
        models_file = os.path.join(current_dir, 'available_models.json')
        with open(models_file, 'r') as f:
            self.available_models = json.load(f)

    def login(self) -> bool:
        """
        Authenticates with Puter.js using the provided username and password.

        Raises:
            PuterAuthError: If username or password are not set, or if login fails.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        if not self._username or not self._password:
            raise PuterAuthError("Username and password must be set for login.")

        payload = {"username": self._username, "password": self._password}
        try:
            response = requests.post(self._login_url, headers=self._headers, json=payload)
            response.raise_for_status()
            data = response.json()
            if data.get("proceed"):
                self._token = data["token"]
                return True
            else:
                raise PuterAuthError("Login failed. Please check your credentials.")
        except requests.RequestException as e:
            raise PuterAuthError(f"Login error: {e}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Gets the authorization headers for API requests.

        Raises:
            PuterAuthError: If not authenticated.

        Returns:
            Dict[str, str]: A dictionary of headers including the authorization token.
        """
        if not self._token:
            raise PuterAuthError("Not authenticated. Please login first.")
        return {
            **self._headers,
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _get_driver_for_model(self, model_name: str) -> str:
        """
        Determines the backend driver for a given model name.

        Args:
            model_name (str): The name of the AI model.

        Returns:
            str: The corresponding driver name (e.g., "claude", "openai-completion").
        """
        return self.available_models.get(model_name, "openai-completion")

    def chat(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Sends a chat message to the AI model and returns its response.

        The conversation history is automatically managed.

        Args:
            prompt (str): The user's message.
            model (Optional[str]): The model to use for this specific chat. Defaults to current_model.

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
            response = requests.post(
                f"{self._api_base}/drivers/call",
                json=payload,
                headers=headers,
                stream=False,
            )
            response.raise_for_status()
            response_data = response.json()
            
            # More robust response parsing with detailed debugging
            def extract_content(data):
                """Extract content from various possible response formats"""
                # Check if data has a result field
                if isinstance(data, dict) and "result" in data:
                    result = data["result"]
                    
                    # Case 1: result.message.content (original expected format)
                    if isinstance(result, dict) and "message" in result:
                        message = result["message"]
                        if isinstance(message, dict) and "content" in message:
                            content = message["content"]
                            if isinstance(content, list):
                                return "".join([item.get("text", "") for item in content if item.get("type") == "text"])
                            elif isinstance(content, str):
                                return content
                    
                    # Case 2: result.content (direct content in result)
                    if isinstance(result, dict) and "content" in result:
                        content = result["content"]
                        if isinstance(content, list):
                            return "".join([item.get("text", "") for item in content if item.get("type") == "text"])
                        elif isinstance(content, str):
                            return content
                    
                    # Case 3: result is directly the content string
                    if isinstance(result, str):
                        return result
                    
                    # Case 4: result.choices[0].message.content (OpenAI-style format)
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
                    "response_keys": list(response_data.keys()) if isinstance(response_data, dict) else "Not a dict",
                    "response_preview": str(response_data)[:200] + "..." if len(str(response_data)) > 200 else str(response_data)
                }
                return f"No content in AI response. Debug: {json.dumps(debug_info, indent=2)}"
        except requests.RequestException as e:
            raise PuterAPIError(f"AI chat error: {e}")

    def clear_chat_history(self):
        """
        Clears the current chat history.
        """
        self.chat_history = []

    def set_model(self, model_name: str) -> bool:
        """
        Sets the current AI model for subsequent chat interactions.

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
        """
        Retrieves a list of all available AI model names.

        Returns:
            List[str]: A list of strings, where each string is an available model name.
        """
        return list(self.available_models.keys())

