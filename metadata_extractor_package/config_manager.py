"""
Simplified configuration management - config.yaml only
"""

import os
import yaml
from pathlib import Path

def get_default_config():
    """Get default configuration with all settings in one place"""
    return {
        'llm': {
            'provider': 'openai',  # 'openai' or 'local'
            'openai': {
                'api_key': 'your-openai-api-key-here',  # Replace with your actual key
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
                'url': 'your-supabase-project-url-here',  # Replace with your actual URL
                'key': 'your-supabase-anon-key-here',      # Replace with your actual key
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
    """Load configuration from config.yaml only"""
    config_path = Path("config.yaml")

    if not config_path.exists():
        print("❌ config.yaml not found. Creating default...")
        create_default_config()
        print("⚠️  Please edit config.yaml with your actual API keys!")

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Validate and provide helpful error messages
        validate_config(config)
        return config

    except Exception as e:
        print(f"❌ Error loading config.yaml: {e}")
        print("Creating default configuration...")
        create_default_config()
        return get_default_config()

def create_default_config():
    """Create a default config.yaml file with clear instructions"""
    config = get_default_config()

    try:
        with open("config.yaml", 'w') as file:
            # Add helpful header comment
            file.write("# Dataset Metadata Extraction Tool Configuration\n")
            file.write("# Edit the values below with your actual credentials\n")
            file.write("# Remove the placeholder text and add your real API keys\n\n")

            yaml.dump(config, file, default_flow_style=False, indent=2)

        print("✅ Created default config.yaml")
        print("\n📝 IMPORTANT: Edit config.yaml and replace placeholder values:")
        print("   - your-openai-api-key-here")
        print("   - your-supabase-project-url-here")
        print("   - your-supabase-anon-key-here")

    except Exception as e:
        print(f"❌ Could not create config.yaml: {e}")

def validate_config(config):
    """Validate configuration and provide helpful warnings"""
    warnings = []
    errors = []

    # Check LLM configuration
    llm_provider = config.get('llm', {}).get('provider', 'openai')

    if llm_provider == 'openai':
        api_key = config.get('llm', {}).get('openai', {}).get('api_key', '')
        if not api_key or api_key == 'your-openai-api-key-here':
            errors.append("OpenAI API key not configured. Please edit config.yaml")

    elif llm_provider == 'local':
        api_url = config.get('llm', {}).get('local', {}).get('api_url', '')
        if not api_url or 'your-ngrok-url' in api_url:
            errors.append("Local LLM API URL not configured. Please edit config.yaml")

    # Check database configuration if enabled
    if config.get('database', {}).get('enabled', False):
        supabase_config = config.get('database', {}).get('supabase', {})
        url = supabase_config.get('url', '')
        key = supabase_config.get('key', '')

        if not url or url == 'your-supabase-project-url-here':
            warnings.append("Supabase URL not configured - cloud features will be disabled")

        if not key or key == 'your-supabase-anon-key-here':
            warnings.append("Supabase key not configured - cloud features will be disabled")

    # Print warnings and errors
    if warnings:
        print("⚠️  Configuration warnings:")
        for warning in warnings:
            print(f"   - {warning}")

    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease edit config.yaml to fix these issues.")

def get_config_info(config):
    """Get current configuration information"""
    provider = config['llm']['provider']
    db_info = ""

    if config.get('database', {}).get('enabled', False):
        db_provider = config['database']['provider']
        db_info = f" | Database: {db_provider.title()}"

    if provider == 'openai':
        model = config['llm']['openai']['model']
        return f"OpenAI ({model}){db_info}"
    elif provider == 'local':
        url = config['llm']['local']['api_url']
        return f"Local LLM ({url}){db_info}"
    else:
        return f"Unknown ({provider}){db_info}"

def get_supabase_credentials(config):
    """Get Supabase credentials from config"""
    if not config.get('database', {}).get('enabled', False):
        return None, None

    supabase_config = config.get('database', {}).get('supabase', {})
    url = supabase_config.get('url')
    key = supabase_config.get('key')

    # Return None if still using placeholder values
    if url == 'your-supabase-project-url-here':
        url = None
    if key == 'your-supabase-anon-key-here':
        key = None

    return url, key

def is_database_enabled(config):
    """Check if database integration is enabled and properly configured"""
    if not config.get('database', {}).get('enabled', False):
        return False

    url, key = get_supabase_credentials(config)
    return url is not None and key is not None

def is_auto_save_enabled(config):
    """Check if auto-save is enabled"""
    return (is_database_enabled(config) and
            config.get('database', {}).get('supabase', {}).get('auto_save', False))

def update_config_value(key_path, value):
    """Update a specific config value and save to file"""
    config_path = Path("config.yaml")

    if not config_path.exists():
        create_default_config()

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Navigate to the nested key and update
        keys = key_path.split('.')
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

        # Save updated config
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False, indent=2)

        print(f"✅ Updated {key_path} in config.yaml")
        return True

    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

# Helper function for easy credential updates
def set_openai_key(api_key):
    """Set OpenAI API key in config"""
    return update_config_value('llm.openai.api_key', api_key)

def set_supabase_credentials(url, key):
    """Set Supabase credentials in config"""
    success = True
    success &= update_config_value('database.supabase.url', url)
    success &= update_config_value('database.supabase.key', key)
    return success

def enable_database(enabled=True):
    """Enable or disable database integration"""
    return update_config_value('database.enabled', enabled)