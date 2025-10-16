#!/usr/bin/env python3
"""
Advanced Configuration Example - Puter Python SDK

Demonstrates all configuration options, environment variables,
and advanced settings for production usage.
"""

import os

from puter import PuterConfig, config


def demonstrate_env_config():
    """Show how to use environment variables for configuration."""
    print("🌍 Environment Variable Configuration")
    print("=" * 45)

    # Set environment variables programmatically (normally done in shell)
    env_vars = {
        "PUTER_API_BASE": "https://api.puter.com",
        "PUTER_TIMEOUT": "45",
        "PUTER_MAX_RETRIES": "5",
        "PUTER_RETRY_DELAY": "2.0",
        "PUTER_BACKOFF_FACTOR": "3.0",
        "PUTER_RATE_LIMIT_REQUESTS": "15",
        "PUTER_RATE_LIMIT_PERIOD": "30",
    }

    print("Setting environment variables:")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  {key}={value}")

    # Create new config to pick up env vars
    new_config = PuterConfig()

    print("\n✅ Configuration loaded from environment:")
    print(f"  • API Base: {new_config.api_base}")
    print(f"  • Timeout: {new_config.timeout}s")
    print(f"  • Max Retries: {new_config.max_retries}")
    print(
        f"  • Rate Limit: {new_config.rate_limit_requests}/{new_config.rate_limit_period}s"
    )


def demonstrate_programmatic_config():
    """Show programmatic configuration options."""
    print("\n⚙️ Programmatic Configuration")
    print("=" * 35)

    # Method 1: Update global config
    print("Method 1: Global config update")
    original_timeout = config.timeout
    config.update(timeout=60, max_retries=7, rate_limit_requests=25)

    print(f"  Updated timeout: {config.timeout}s")
    print(f"  Updated max retries: {config.max_retries}")
    print(f"  Updated rate limit: {config.rate_limit_requests}")

    # Method 2: Client-specific overrides
    print("\nMethod 2: Client-specific overrides")
    # Example of client-specific overrides:
    # client = PuterAI(
    #     username="demo",
    #     password="demo",
    #     timeout=90,
    #     max_retries=10,
    #     rate_limit_requests=50,
    #     rate_limit_period=120,
    # )

    print("  ✅ Client created with custom settings")

    # Restore original config
    config.update(timeout=original_timeout)


def demonstrate_config_profiles():
    """Show different configuration profiles for different use cases."""
    print("\n📋 Configuration Profiles")
    print("=" * 30)

    profiles = {
        "development": {
            "timeout": 30,
            "max_retries": 3,
            "rate_limit_requests": 10,
            "rate_limit_period": 60,
        },
        "production": {
            "timeout": 60,
            "max_retries": 5,
            "rate_limit_requests": 100,
            "rate_limit_period": 3600,
        },
        "batch_processing": {
            "timeout": 120,
            "max_retries": 10,
            "rate_limit_requests": 1000,
            "rate_limit_period": 3600,
        },
        "testing": {
            "timeout": 10,
            "max_retries": 1,
            "rate_limit_requests": 5,
            "rate_limit_period": 60,
        },
    }

    for profile_name, settings in profiles.items():
        print(f"\n🎯 {profile_name.title()} Profile:")
        for key, value in settings.items():
            print(f"    {key}: {value}")

        # Show how to apply profile
        print(f"  Usage: PuterAI(username='...', password='...', **{settings})")


def demonstrate_monitoring_config():
    """Show configuration for monitoring and debugging."""
    print("\n🔍 Monitoring & Debugging Configuration")
    print("=" * 42)

    # Custom headers for tracking
    custom_headers = {
        "X-Client-Version": "puter-python-sdk-0.2.0",
        "X-Environment": "production",
        "X-Service": "content-generator",
    }

    print("Custom headers for request tracking:")
    for key, value in custom_headers.items():
        print(f"  {key}: {value}")

    # You would extend the config class to support custom headers
    print("\n💡 Tip: Extend PuterConfig class for custom monitoring")


def main():
    """Run all configuration demonstrations."""
    print("⚙️ Advanced Configuration - Puter Python SDK")
    print("=" * 55)

    demonstrate_env_config()
    demonstrate_programmatic_config()
    demonstrate_config_profiles()
    demonstrate_monitoring_config()

    print("\n" + "=" * 55)
    print("🎉 Configuration Examples Complete!")
    print("\n💡 Key Takeaways:")
    print("• Use environment variables for production deployments")
    print("• Override settings per client for specific use cases")
    print("• Choose appropriate profiles based on your needs")
    print("• Monitor performance and adjust settings accordingly")
    print("\n📚 Next: Explore error_handling.py and rate_limiting_demo.py")


if __name__ == "__main__":
    main()
