# Puter Python SDK Examples

This directory contains practical examples demonstrating how to use the Puter Python SDK to access free AI models.

## 📁 Example Categories

### 🤖 Basic Usage
- [`basic_chat.py`](basic_chat.py) - Simple chat interaction
- [`model_switching.py`](model_switching.py) - How to switch between different AI models
- [`async_usage.py`](async_usage.py) - Using async/await features

### 💬 Chatbots & Conversational AI
- [`simple_chatbot.py`](chatbots/simple_chatbot.py) - Basic interactive chatbot
- [`personality_bot.py`](chatbots/personality_bot.py) - AI with custom personality
- [`multi_model_bot.py`](chatbots/multi_model_bot.py) - Bot that uses multiple models

### ✍️ Content Generation
- [`blog_writer.py`](content_generation/blog_writer.py) - Automated blog post generation
- [`code_generator.py`](content_generation/code_generator.py) - AI-powered code generation
- [`creative_writing.py`](content_generation/creative_writing.py) - Stories, poems, and creative content

### 🔄 Workflow Automation
- [`batch_processing.py`](workflows/batch_processing.py) - Process multiple tasks efficiently
- [`content_pipeline.py`](workflows/content_pipeline.py) - Multi-stage content creation
- [`data_analysis.py`](workflows/data_analysis.py) - AI-powered data insights

### 🧪 Advanced Features
- [`rate_limiting_demo.py`](advanced/rate_limiting_demo.py) - Demonstrate rate limiting
- [`error_handling.py`](advanced/error_handling.py) - Robust error handling patterns
- [`configuration.py`](advanced/configuration.py) - Advanced configuration options

### 📊 Jupyter Notebooks
- [`getting_started.ipynb`](notebooks/getting_started.ipynb) - Interactive tutorial
- [`model_comparison.ipynb`](notebooks/model_comparison.ipynb) - Compare different AI models
- [`advanced_features.ipynb`](notebooks/advanced_features.ipynb) - Deep dive into SDK features

## 🚀 Quick Start

1. **Install the SDK:**
   ```bash
   pip install puter-python-sdk
   ```

2. **Set up authentication:**
   ```python
   from puter import PuterAI
   
   # Method 1: Direct credentials
   client = PuterAI(username="your_username", password="your_password")
   client.login()
   
   # Method 2: Environment variables
   # Set PUTER_USERNAME and PUTER_PASSWORD
   client = PuterAI()
   client.login()
   ```

3. **Start chatting:**
   ```python
   response = client.chat("Hello! How are you today?")
   print(response)
   ```

## 🔧 Configuration Examples

### Environment Variables
```bash
export PUTER_API_BASE="https://api.puter.com"
export PUTER_TIMEOUT="30"
export PUTER_MAX_RETRIES="3"
export PUTER_RATE_LIMIT_REQUESTS="10"
export PUTER_RATE_LIMIT_PERIOD="60"
```

### Programmatic Configuration
```python
from puter import PuterAI, config

# Override default settings
client = PuterAI(
    username="your_username",
    password="your_password",
    timeout=60,
    max_retries=5,
    rate_limit_requests=20
)
```

## 📝 Contributing Examples

Have a cool use case? We'd love to see it! Please:

1. Create a new file in the appropriate category
2. Include clear comments and documentation
3. Add error handling and best practices
4. Update this README with your example
5. Submit a pull request

## 🆘 Need Help?

- 📚 [Main Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/CuzImSlymi/puter-python-sdk/issues)
- 💬 [Discussions](https://github.com/CuzImSlymi/puter-python-sdk/discussions)