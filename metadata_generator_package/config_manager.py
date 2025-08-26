"""
Configuration Management for Dataset Metadata Extraction Tool

Handles loading and validating configuration from config.yaml.
Supports OpenAI and local LLM providers, plus optional Supabase integration.
"""

import os
import yaml
from pathlib import Path


def get_default_config():
    """Get default configuration with placeholder values."""
    return {
        'llm': {
            'provider': 'openai',  # 'openai' or 'local'
            'openai': {
                'api_key': 'your-openai-api-key-here',
                'model': 'gpt-3.5-turbo',
                'max_tokens': 300,
                'temperature': 0.7,
                'timeout': 30
            },
            'local': {
                'api_url': 'https://your-ngrok-url.ngrok-free.app/generate',
                'max_tokens': 300,
                'temperature': 0.7,
                'timeout': 30,
                'headers': {
                    'Content-Type': 'application/json',
                    'ngrok-skip-browser-warning': 'true'
                }
            }
        },
        'app': {
            'debug': False,
            'max_file_size_mb': 30,
            'session_cleanup_hours': 1
        },
        'database': {
            'enabled': True,
            'provider': 'supabase',
            'supabase': {
                'url': 'your-supabase-project-url-here',
                'key': 'your-supabase-anon-key-here',
                'auto_save': True,
                'bucket_name': 'dataset-metadata'
            }
        },
        'logging': {
            'level': 'INFO',
            'show_prompts': True
        }
    }


def load_config():
    """Load configuration from config.yaml. Creates default if missing."""
    config_path = Path("config.yaml")

    # Create default config if file doesn't exist
    if not config_path.exists():
        print("⚠️ config.yaml not found. Creating default...")
        create_default_config()
        print("🔧 Please edit config.yaml with your actual API keys!")

    # Load existing config
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file) or {}

        # Check for common configuration issues
        validate_config(config)
        return config

    except Exception as e:
        # Fall back to defaults if loading fails
        print(f"❌ Error loading config.yaml: {e}")
        print("📝 Creating default configuration...")
        create_default_config()
        return get_default_config()


def create_default_config():
    """Create a default config.yaml file with placeholder values."""
    config = get_default_config()

    try:
        with open("config.yaml", 'w', encoding='utf-8') as file:
            # Add helpful header comments
            file.write("# Dataset Metadata Extraction Tool Configuration\n")
            file.write("# Edit the values below with your actual credentials\n")
            file.write("# Remove the placeholder text and add your real API keys\n\n")

            yaml.dump(config, file, default_flow_style=False, indent=2)

        print("✅ Created default config.yaml")
        _print_setup_instructions()

    except Exception as e:
        print(f"❌ Could not create config.yaml: {e}")
        raise


def validate_config(config):
    """Check configuration and show warnings for common issues."""
    warnings = []  # Non-critical issues
    errors = []    # Critical issues

    llm_provider = config.get('llm', {}).get('provider', 'openai')

    # Check LLM configuration
    if llm_provider == 'openai':
        api_key = config.get('llm', {}).get('openai', {}).get('api_key', '')
        if _is_placeholder_value(api_key, 'your-openai-api-key-here'):
            errors.append("OpenAI API key not configured. Please edit config.yaml")

    elif llm_provider == 'local':
        api_url = config.get('llm', {}).get('local', {}).get('api_url', '')
        if _is_placeholder_value(api_url, 'your-ngrok-url'):
            errors.append("Local LLM API URL not configured. Please edit config.yaml")
    else:
        warnings.append(f"Unknown LLM provider: {llm_provider}")

    # Check database configuration if enabled
    if config.get('database', {}).get('enabled', False):
        supabase_config = config.get('database', {}).get('supabase', {})
        url = supabase_config.get('url', '')
        key = supabase_config.get('key', '')

        if _is_placeholder_value(url, 'your-supabase-project-url-here'):
            warnings.append("Supabase URL not configured - cloud features will be disabled")

        if _is_placeholder_value(key, 'your-supabase-anon-key-here'):
            warnings.append("Supabase key not configured - cloud features will be disabled")

    # Show validation results
    _print_validation_results(warnings, errors)


def get_config_info(config):
    """Get a summary of the current configuration."""
    provider = config.get('llm', {}).get('provider', 'unknown')

    # Build LLM info string
    if provider == 'openai':
        model = config.get('llm', {}).get('openai', {}).get('model', 'unknown')
        llm_info = f"OpenAI ({model})"
    elif provider == 'local':
        url = config.get('llm', {}).get('local', {}).get('api_url', 'unknown')
        llm_info = f"Local LLM ({url})"
    else:
        llm_info = f"Unknown ({provider})"

    # Add database info if configured
    if is_database_enabled(config):
        db_provider = config.get('database', {}).get('provider', 'unknown')
        db_info = f" | Database: {db_provider.title()}"
    else:
        db_info = ""

    return f"{llm_info}{db_info}"


def get_supabase_credentials(config):
    """Get Supabase URL and key from config. Returns (None, None) if not configured."""
    if not config.get('database', {}).get('enabled', False):
        return None, None

    supabase_config = config.get('database', {}).get('supabase', {})
    url = supabase_config.get('url')
    key = supabase_config.get('key')

    # Return None for placeholder values
    if _is_placeholder_value(url, 'your-supabase-project-url-here'):
        url = None
    if _is_placeholder_value(key, 'your-supabase-anon-key-here'):
        key = None

    return url, key


def is_database_enabled(config):
    """Check if database integration is properly configured."""
    if not config.get('database', {}).get('enabled', False):
        return False

    url, key = get_supabase_credentials(config)
    return url is not None and key is not None


def is_auto_save_enabled(config):
    """Check if automatic cloud saving is enabled."""
    return (is_database_enabled(config) and
            config.get('database', {}).get('supabase', {}).get('auto_save', False))


# Private helper functions

def _is_placeholder_value(value, placeholder_substring):
    """Check if a config value is still a placeholder."""
    if not value:
        return True
    return placeholder_substring in str(value)


def _print_validation_results(warnings, errors):
    """Print configuration warnings and errors."""
    if warnings:
        print("⚠️  Configuration warnings:")
        for warning in warnings:
            print(f"   - {warning}")

    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        print("\n📝 Please edit config.yaml to fix these issues.")


def _print_setup_instructions():
    """Print setup instructions for new users."""
    print("\n🔧 IMPORTANT: Edit config.yaml and replace placeholder values:")
    print("   - your-openai-api-key-here")
    print("   - your-supabase-project-url-here")
    print("   - your-supabase-anon-key-here")
    print("\n📚 To get your credentials:")
    print("   - OpenAI: https://platform.openai.com/api-keys")
    print("   - Supabase: https://supabase.com → Your Project → Settings → API")