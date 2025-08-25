#!/usr/bin/env python3
"""
Improved Database Setup Script for Dataset Metadata Extraction Tool
This script helps you set up the Supabase database with better error handling
"""

import os
import sys
import yaml
import re
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("📊 Dataset Metadata Extraction Tool - Database Setup")
    print("=" * 60)
    print()

def check_supabase_installed():
    """Check if Supabase package is installed"""
    try:
        import supabase
        print("✅ Supabase package is installed")
        return True
    except ImportError:
        print("❌ Supabase package not found!")
        print("Please install it first:")
        print("  pip install supabase")
        print()
        return False

def validate_supabase_url(url):
    """Validate Supabase URL format"""
    if not url:
        return False, "URL is empty"

    # Check for placeholder
    if url == "https://your-project.supabase.co":
        return False, "Using placeholder URL - please update with your actual Supabase URL"

    # Check URL format
    pattern = r'^https://[a-zA-Z0-9-]+\.supabase\.co$'
    if not re.match(pattern, url):
        return False, "Invalid Supabase URL format. Should be: https://your-project.supabase.co"

    return True, "Valid URL format"

def validate_supabase_key(key):
    """Validate Supabase key format"""
    if not key:
        return False, "Key is empty"

    # Check for placeholder
    if key == "your-supabase-anon-key":
        return False, "Using placeholder key - please update with your actual Supabase key"

    # Supabase keys are typically JWT tokens starting with 'eyJ'
    if not key.startswith('eyJ'):
        return False, "Invalid Supabase key format. Should start with 'eyJ'"

    return True, "Valid key format"

def get_credentials_from_env():
    """Get credentials from environment variables"""
    url = os.getenv('SUPABASE_URL', '')
    key = os.getenv('SUPABASE_KEY', '')

    if url and key:
        print("🔐 Found Supabase credentials in environment variables")
        return url, key

    return None, None

def prompt_for_credentials():
    """Prompt user for Supabase credentials"""
    print("🔧 Let's set up your Supabase credentials!")
    print()

    print("First, you need to create a Supabase project:")
    print("1. Go to https://supabase.com")
    print("2. Sign up for a free account")
    print("3. Create a new project")
    print("4. Go to Settings → API")
    print()

    # Get URL
    while True:
        url = input("Enter your Supabase Project URL: ").strip()
        is_valid, message = validate_supabase_url(url)
        if is_valid:
            break
        print(f"❌ {message}")
        print("Example: https://abcdefghijklmnop.supabase.co")
        print()

    # Get Key
    while True:
        key = input("Enter your Supabase anon key: ").strip()
        is_valid, message = validate_supabase_key(key)
        if is_valid:
            break
        print(f"❌ {message}")
        print("The key should be a long string starting with 'eyJ'")
        print()

    return url, key

def update_config_file(url, key):
    """Update config.yaml with Supabase credentials"""
    config_path = Path("config.yaml")

    # Load existing config or create new one
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # Update database section
    if 'database' not in config:
        config['database'] = {}

    config['database']['enabled'] = True
    config['database']['provider'] = 'supabase'

    if 'supabase' not in config['database']:
        config['database']['supabase'] = {}

    config['database']['supabase']['url'] = url
    config['database']['supabase']['key'] = key
    config['database']['supabase']['auto_save'] = True
    config['database']['supabase']['bucket_name'] = 'dataset-metadata'

    # Save updated config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

    print(f"✅ Updated {config_path} with Supabase credentials")

def test_connection(url, key):
    """Test connection to Supabase"""
    try:
        print("🧪 Testing Supabase connection...")

        # Import and create client
        from supabase import create_client
        client = create_client(url, key)

        # Test basic connection with a simple query
        print("  → Testing database connection...")
        try:
            # Try to run a simple query
            result = client.rpc('version').execute()
            print("  ✅ Database connection successful!")
        except Exception as e:
            # If RPC fails, try a table query (will fail if table doesn't exist, but connection works)
            try:
                client.table('dataset_metadata').select('count').limit(1).execute()
                print("  ✅ Database connection successful!")
            except Exception as e2:
                if "relation" in str(e2) and "does not exist" in str(e2):
                    print("  ✅ Database connection successful! (Table not created yet)")
                else:
                    print(f"  ❌ Database connection failed: {e2}")
                    return False

        # Test storage connection
        print("  → Testing storage connection...")
        try:
            buckets = client.storage.list_buckets()
            print("  ✅ Storage connection successful!")

            # Check if bucket exists
            bucket_exists = any(bucket.name == 'dataset-metadata' for bucket in buckets)
            if bucket_exists:
                print("  ✅ Storage bucket 'dataset-metadata' exists!")
            else:
                print("  ⚠️  Storage bucket 'dataset-metadata' not found!")
                print("     You'll need to create it in the Supabase dashboard")

        except Exception as e:
            print(f"  ❌ Storage connection failed: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def print_sql_setup():
    """Print SQL setup instructions"""
    print()
    print("📋 Database Setup Instructions:")
    print("=" * 40)
    print()
    print("1. Go to your Supabase dashboard")
    print("2. Click on 'SQL Editor' in the left sidebar")
    print("3. Click 'New Query' and paste the following SQL:")
    print()
    print("-- Create dataset_metadata table")
    print("""
CREATE TABLE IF NOT EXISTS dataset_metadata (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    dataset_name VARCHAR(500) NOT NULL,
    dataset_description TEXT,
    original_filename VARCHAR(500),
    column_count INTEGER DEFAULT 0,
    metadata_json JSONB,
    file_url TEXT,
    storage_path VARCHAR(500),
    file_size BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_file_id ON dataset_metadata(file_id);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_session_id ON dataset_metadata(session_id);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_created_at ON dataset_metadata(created_at);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_dataset_name ON dataset_metadata(dataset_name);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_dataset_metadata_updated_at 
    BEFORE UPDATE ON dataset_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
""")
    print()
    print("4. Click 'Run' to execute the SQL")
    print()

def print_storage_setup():
    """Print storage setup instructions"""
    print("📦 Storage Setup Instructions:")
    print("=" * 40)
    print()
    print("1. Go to your Supabase dashboard")
    print("2. Click on 'Storage' in the left sidebar")
    print("3. Click 'Create bucket'")
    print("4. Enter bucket name: 'dataset-metadata'")
    print("5. Set it to 'Private' (recommended)")
    print("6. Click 'Create bucket'")
    print()

def print_success_message():
    """Print success message"""
    print()
    print("🎉 Setup Complete!")
    print("=" * 20)
    print()
    print("Your Supabase database is now configured!")
    print()
    print("Next steps:")
    print("1. Run the SQL commands above in your Supabase SQL Editor")
    print("2. Create the storage bucket as described")
    print("3. Start your application: python app.py")
    print("4. Upload and analyze a dataset to test the integration")
    print()

def main():
    """Main setup function"""
    print_header()

    # Check if Supabase is installed
    if not check_supabase_installed():
        return

    # Try to get credentials from environment first
    url, key = get_credentials_from_env()

    if not url or not key:
        # Check if config.yaml exists and has valid credentials
        config_path = Path("config.yaml")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)

                supabase_config = config.get('database', {}).get('supabase', {})
                config_url = supabase_config.get('url', '')
                config_key = supabase_config.get('key', '')

                # Validate config credentials
                url_valid, url_msg = validate_supabase_url(config_url)
                key_valid, key_msg = validate_supabase_key(config_key)

                if url_valid and key_valid:
                    url, key = config_url, config_key
                    print("✅ Found valid Supabase credentials in config.yaml")
                else:
                    print("❌ Invalid credentials in config.yaml:")
                    if not url_valid:
                        print(f"  URL: {url_msg}")
                    if not key_valid:
                        print(f"  Key: {key_msg}")
                    print()
                    url, key = prompt_for_credentials()
                    update_config_file(url, key)
            except Exception as e:
                print(f"❌ Error reading config.yaml: {e}")
                url, key = prompt_for_credentials()
                update_config_file(url, key)
        else:
            # No config file, prompt for credentials
            url, key = prompt_for_credentials()
            update_config_file(url, key)

    # Test connection
    if test_connection(url, key):
        print_success_message()
        print_sql_setup()
        print_storage_setup()
    else:
        print()
        print("❌ Setup failed!")
        print("Please check your credentials and try again.")
        print()
        print("Common issues:")
        print("- Make sure your Supabase project is active")
        print("- Check if your URL and key are correct")
        print("- Ensure you have internet connection")
        print("- Try creating a new anon key in Supabase dashboard")

if __name__ == "__main__":
    main()