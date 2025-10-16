# Contributing to Puter Python SDK

Thank you for your interest in contributing to the Puter Python SDK! This guide will help you get started with contributing to our project.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Install dependencies** and set up development environment
4. **Make your changes** following our guidelines
5. **Test your changes** thoroughly
6. **Submit a pull request**

## 🛠️ Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- A Puter.js account for testing

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/puter-python-sdk.git
cd puter-python-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Environment Variables

Set up your test environment:

```bash
export PUTER_USERNAME="your_test_username"
export PUTER_PASSWORD="your_test_password"
```

## 📝 Code Guidelines

### Code Style

We follow Python community standards:

- **PEP 8** for code style
- **Black** for code formatting
- **Type hints** for better code documentation
- **Docstrings** for all public functions and classes

### Running Code Quality Checks

```bash
# Format code
black puter/

# Check linting
flake8 puter/

# Type checking
mypy puter/

# Run all checks
python -m pytest --cov=puter tests/
```

### Code Structure

```
puter/
├── __init__.py          # Package initialization and exports
├── ai.py               # Main PuterAI class
├── config.py           # Configuration management
├── exceptions.py       # Custom exceptions
└── available_models.json  # Supported AI models
```

## 🧪 Testing

### Writing Tests

- Place tests in the `tests/` directory
- Use `pytest` for testing framework
- Include both unit tests and integration tests
- Test both sync and async functionality

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=puter

# Run specific test file
python -m pytest tests/test_ai.py

# Run tests with verbose output
python -m pytest -v
```

### Test Structure

```python
import pytest
from puter import PuterAI
from puter.exceptions import PuterAuthError

def test_initialization():
    """Test PuterAI initialization."""
    client = PuterAI(username="test", password="test")
    assert client.current_model == "claude-opus-4"

@pytest.mark.asyncio
async def test_async_functionality():
    """Test async operations."""
    # Your async test code here
    pass
```

## 📚 Documentation

### API Documentation

- Use **Google-style docstrings** for all public APIs
- Include **type hints** for parameters and return values
- Provide **examples** in docstrings when helpful

Example:
```python
def chat(self, prompt: str, model: Optional[str] = None) -> str:
    """Send a chat message to the AI model and returns its response.

    The conversation history is automatically managed.

    Args:
        prompt (str): The user's message.
        model (Optional[str]): The model to use for this specific chat.
            Defaults to current_model.

    Returns:
        str: The AI's response as a string.

    Raises:
        PuterAPIError: If the API call fails.
        PuterAuthError: If not authenticated.

    Example:
        >>> client = PuterAI(username="user", password="pass")
        >>> client.login()
        >>> response = client.chat("Hello, how are you?")
        >>> print(response)
        Hello! I'm doing well, thank you for asking...
    """
```

### Examples

When adding new features, please include:

- **Basic usage example** in the feature's docstring
- **Comprehensive example** in the `examples/` directory
- **Jupyter notebook** demonstration if applicable

## 🐛 Bug Reports

### Before Submitting

1. **Search existing issues** to avoid duplicates
2. **Try the latest version** to see if the issue is fixed
3. **Provide minimal reproduction** case

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Initialize client with '...'
2. Call method '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g. 3.9.0]
- SDK version: [e.g. 0.3.0]

**Code Sample**
```python
# Minimal code that reproduces the issue
from puter import PuterAI
# ... your code here
```

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Before Submitting

1. **Check if the feature already exists** in the latest version
2. **Search existing feature requests** to avoid duplicates
3. **Consider if it fits the project scope**

### Feature Request Template

```markdown
**Feature Description**
A clear description of what you want to happen.

**Use Case**
Describe the use case and why this feature would be useful.

**Proposed API**
If you have ideas about the API design:

```python
# Example of how the feature might work
client.new_feature(param="value")
```

**Alternatives Considered**
Other ways you've considered solving this problem.
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create an issue** to discuss major changes
2. **Fork the repository** and create a feature branch
3. **Follow code style guidelines**
4. **Add tests** for new functionality
5. **Update documentation** as needed

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Self-review of code completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear and descriptive

### Pull Request Template

```markdown
**Description**
Brief description of what this PR does.

**Type of Change**
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

**Testing**
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

**Related Issues**
Fixes #(issue number)

**Screenshots/Examples**
If applicable, add screenshots or code examples.
```

## 📋 Code Review Process

### For Contributors

- **Be open to feedback** and suggestions
- **Respond promptly** to review comments
- **Make requested changes** in a timely manner
- **Ask questions** if feedback is unclear

### For Reviewers

- **Be constructive** and helpful in feedback
- **Focus on code quality** and adherence to guidelines
- **Test the changes** if possible
- **Approve when ready** or request specific changes

## 🏷️ Release Process

### Version Numbers

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Release Steps

1. Update version numbers in `__init__.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create release commit and tag
4. Build and publish to PyPI
5. Create GitHub release with release notes

## 🤝 Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive
- **Help others** learn and contribute
- **Give constructive feedback**
- **Credit others** for their contributions

### Communication

- **GitHub Issues** for bug reports and feature requests
- **GitHub Discussions** for questions and general discussion
- **Pull Request comments** for code-specific discussion

## ❓ Getting Help

### Documentation

- [README.md](README.md) - Project overview and basic usage
- [API Documentation](docs/api.md) - Detailed API reference
- [Examples](examples/) - Practical usage examples

### Support Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and community support
- **Email** - justin@slymi.org for private inquiries

## 🙏 Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **CHANGELOG.md** release notes
- **GitHub releases** acknowledgments

Thank you for contributing to the Puter Python SDK! 🎉
