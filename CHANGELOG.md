# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-10-19

### Added
- Complete CI/CD pipeline with GitHub Actions workflows
- Comprehensive test suite with 55+ test cases and coverage reporting
- Multi-platform testing across Windows, macOS, and Ubuntu (Python 3.8-3.12, PyPy)
- Nightly builds with performance monitoring and security auditing
- Pre-commit hooks for automated code quality enforcement
- Code style automation with Black, Flake8, MyPy, isort, and Bandit
- Docstring coverage tracking with interrogate
- Automated dependency updates and vulnerability scanning

### Changed
- Complete code quality overhaul with consistent formatting and linting
- Improved dependency management with clean requirements structure
- Enhanced development experience with automated tooling
- Production-ready infrastructure and quality assurance

### Fixed
- Dependency resolution issues in CI/CD pipeline
- Code style inconsistencies across the codebase
- Missing test coverage for critical functionality


## [0.4.0] - 2025-10-15

### Added
- Enhanced error handling and debugging capabilities
- Improved API response parsing for better reliability
- Additional model support and compatibility

### Changed
- Refined authentication flow
- Better error messages and user feedback
- Performance optimizations

### Fixed
- Edge cases in API response handling
- Authentication token management issues


## [0.3.0] - 2025-10-15

### Added
- Expanded model switching functionality
- Better chat history management
- Enhanced UTF-8 encoding support

### Changed
- Improved model listing and selection
- Refined API interaction patterns
- Better response format handling

### Fixed
- Model switching edge cases
- Chat history persistence issues


## [0.2.0] - 2025-10-15

### Added
- Enhanced chat completion functionality
- Improved model compatibility
- Better error handling for network issues

### Changed
- Refined API communication protocols
- Improved response parsing reliability
- Enhanced debugging information

### Fixed
- API response format inconsistencies
- Connection timeout handling


## [0.1.0] - 2025-10-15

### Added
- Initial release of Puter Python SDK
- Support for all available AI models through Puter.js
- Robust response parsing for multiple API response formats
- Comprehensive error handling and debugging
- Chat history management
- Model switching functionality
- UTF-8 encoding support for installation

### Features
- Login authentication with Puter.js
- Chat completion with various AI models
- Model listing and switching
- Clear chat history functionality
- Detailed error messages and debugging information

### Supported Models
- Claude Opus 4
- Claude Sonnet 4
- GPT-4 variants
- And many more through Puter.js API
