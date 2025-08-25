"""
Optimized configuration management
"""

import os
import yaml
from pathlib import Path

def get_default_config():
    """Get default configuration"""
    return {
        'llm': {
            'provider': 'openai',
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here'),
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
            'debug': True,
            'max_file_size_mb': 30,
            'session_cleanup_hours': 1
        },
        'logging': {
            'level': 'INFO',
            'show_prompts': True
        },
        'database': {
            'enabled': True,
            'provider': 'supabase',
            'supabase': {
                'url': os.getenv('SUPABASE_URL', 'https://your-project.supabase.co'),
                'key': os.getenv('SUPABASE_KEY', 'your-supabase-anon-key'),
                'auto_save': True,
                'bucket_name': 'dataset-metadata'
            }
        }
    }

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path("config.yaml")

    if not config_path.exists():
        print("❌ config.yaml not found. Creating default...")
        create_default_config()

    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"❌ Error loading config.yaml: {e}")
        return get_default_config()

def create_default_config():
    """Create a default config.yaml file"""
    try:
        with open("config.yaml", 'w') as file:
            yaml.dump(get_default_config(), file, default_flow_style=False, indent=2)
        print("✅ Created default config.yaml")
    except Exception as e:
        print(f"❌ Could not create config.yaml: {e}")

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

def validate_supabase_config(config):
    """Validate Supabase configuration"""
    if not config.get('database', {}).get('enabled', False):
        return True, "Database disabled"

    supabase_config = config.get('database', {}).get('supabase', {})
    url = supabase_config.get('url', '')
    key = supabase_config.get('key', '')

    # Check for placeholder values
    placeholder_url = 'https://your-project.supabase.co'
    placeholder_key = 'your-supabase-anon-key'

    if not url or url == placeholder_url:
        return False, "Invalid Supabase URL. Please set SUPABASE_URL environment variable or update config.yaml"

    if not key or key == placeholder_key:
        return False, "Invalid Supabase key. Please set SUPABASE_KEY environment variable or update config.yaml"

    return True, "Supabase configuration valid"

def get_supabase_credentials(config):
    """Get Supabase credentials from config"""
    if not config.get('database', {}).get('enabled', False):
        return None, None

    supabase_config = config.get('database', {}).get('supabase', {})
    return supabase_config.get('url'), supabase_config.get('key')

def is_database_enabled(config):
    """Check if database integration is enabled"""
    return config.get('database', {}).get('enabled', False)

def is_auto_save_enabled(config):
    """Check if auto-save is enabled"""
    return config.get('database', {}).get('supabase', {}).get('auto_save', False)