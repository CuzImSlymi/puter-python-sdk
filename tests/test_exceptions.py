"""Tests for custom exceptions."""

import pytest

from puter.exceptions import PuterAPIError, PuterAuthError, PuterError


class TestPuterExceptions:
    """Test custom exception classes."""

    def test_puter_error_base_class(self):
        """Test PuterError as base exception."""
        error = PuterError("Test error")

        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_puter_auth_error_inheritance(self):
        """Test PuterAuthError inherits from PuterError."""
        error = PuterAuthError("Authentication failed")

        assert str(error) == "Authentication failed"
        assert isinstance(error, PuterError)
        assert isinstance(error, Exception)

    def test_puter_api_error_inheritance(self):
        """Test PuterAPIError inherits from PuterError."""
        error = PuterAPIError("API call failed")

        assert str(error) == "API call failed"
        assert isinstance(error, PuterError)
        assert isinstance(error, Exception)

    def test_exception_with_no_message(self):
        """Test exceptions can be created without message."""
        auth_error = PuterAuthError()
        api_error = PuterAPIError()
        base_error = PuterError()

        # Should not raise any errors
        assert isinstance(auth_error, PuterAuthError)
        assert isinstance(api_error, PuterAPIError)
        assert isinstance(base_error, PuterError)

    def test_exception_chaining(self):
        """Test exception chaining with raise from."""
        original_error = ValueError("Original error")

        try:
            raise PuterAPIError("API failed") from original_error
        except PuterAPIError as e:
            assert e.__cause__ is original_error
            assert str(e) == "API failed"

    def test_exception_in_try_except_blocks(self):
        """Test exceptions work correctly in try-except blocks."""
        # Test catching specific exception
        with pytest.raises(PuterAuthError):
            raise PuterAuthError("Auth failed")

        with pytest.raises(PuterAPIError):
            raise PuterAPIError("API failed")

        # Test catching base exception
        with pytest.raises(PuterError):
            raise PuterAuthError("Auth failed")

        with pytest.raises(PuterError):
            raise PuterAPIError("API failed")

    def test_exception_with_complex_message(self):
        """Test exceptions with complex error messages."""
        complex_message = {
            "error_code": 401,
            "message": "Unauthorized access",
            "details": ["Invalid token", "Token expired"],
        }

        error = PuterAuthError(str(complex_message))
        assert str(complex_message) in str(error)
