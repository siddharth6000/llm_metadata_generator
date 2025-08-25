import argparse
import pandas as pd
import json
import random
import sys
import re
import numpy as np
import os
import yaml
import requests
from pathlib import Path

# Try to import OpenAI (optional)
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI library not installed. Install with: pip install openai")


# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found. Creating default configuration...")
        create_default_config()

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"❌ Error loading config.yaml: {e}")
        print("Using default configuration...")
        return get_default_config()


def create_default_config():
    """Create a default config.yaml file"""
    default_config = get_default_config()
    try:
        with open("config.yaml", 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False, indent=2)
        print("✅ Created default config.yaml file. Please update it with your settings.")
    except Exception as e:
        print(f"❌ Could not create config.yaml: {e}")


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
            'max_file_size_mb': 16,
            'session_cleanup_hours': 1
        },
        'logging': {
            'level': 'INFO',
            'show_prompts': True
        }
    }


# Global configuration
CONFIG = load_config()

# Initialize OpenAI client if using OpenAI provider
openai_client = None
if CONFIG['llm']['provider'] == 'openai' and OPENAI_AVAILABLE:
    try:
        api_key = CONFIG['llm']['openai']['api_key']
        if api_key == 'your-openai-api-key-here':
            # Try environment variable
            api_key = os.getenv('OPENAI_API_KEY')

        if api_key:
            openai_client = OpenAI(api_key=api_key)
        else:
            print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable or update config.yaml")
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")


def test_llm_connection():
    """Test if the configured LLM is working"""
    provider = CONFIG['llm']['provider']
    print(f"🧪 Testing {provider.upper()} connection...")

    test_prompt = f"Hello, please respond with '{provider.upper()} is working correctly'."
    response = query_llm(test_prompt, max_tokens=50, temperature=0.1)
    print(f"🧪 Test response: {response}")
    return not (response.startswith("[") and response.endswith("]"))


def query_llm(prompt, max_tokens=None, temperature=None):
    """
    Universal LLM query function that routes to the configured provider
    """
    provider = CONFIG['llm']['provider']

    # Use config defaults if not specified
    if max_tokens is None:
        max_tokens = CONFIG['llm'][provider]['max_tokens']
    if temperature is None:
        temperature = CONFIG['llm'][provider]['temperature']

    if CONFIG['logging']['show_prompts']:
        print(f"\n🌐 Making {provider.upper()} API call...")
        print(f"📝 Prompt length: {len(prompt)} characters")
        print(f"⚙️  Parameters: max_tokens={max_tokens}, temperature={temperature}")

    if provider == 'openai':
        return query_openai_llm(prompt, max_tokens, temperature)
    elif provider == 'local':
        return query_local_llm(prompt, max_tokens, temperature)
    else:
        return f"[Error: Unknown LLM provider '{provider}']"


def query_openai_llm(prompt, max_tokens=300, temperature=0.7):
    """Query OpenAI API for AI responses"""
    if not OPENAI_AVAILABLE:
        return "[Error: OpenAI library not installed]"

    if not openai_client:
        return "[Error: OpenAI client not initialized]"

    try:
        config = CONFIG['llm']['openai']

        if CONFIG['logging']['show_prompts']:
            print(f"📤 Sending request to OpenAI ({config['model']})...")

        response = openai_client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=config['timeout']
        )

        if CONFIG['logging']['show_prompts']:
            print(f"📊 Response received successfully")

        llm_response = response.choices[0].message.content.strip()

        if not llm_response:
            print(f"⚠️  Warning: Empty response from OpenAI")
            return "[Empty OpenAI response]"

        if CONFIG['logging']['show_prompts']:
            print(f"✅ Final OpenAI response: {llm_response[:200]}...")
        return llm_response

    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return f"[OpenAI API error: {str(e)}]"


def query_local_llm(prompt, max_tokens=300, temperature=0.7):
    """Query the local/hosted LLM server for AI responses"""
    config = CONFIG['llm']['local']
    api_url = config['api_url']

    if CONFIG['logging']['show_prompts']:
        print(f"📤 Sending request to local LLM: {api_url}")

    try:
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        headers = config.get('headers', {})

        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=config['timeout']
        )

        if CONFIG['logging']['show_prompts']:
            print(f"📊 Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response content: {response.text}")
            return f"[HTTP Error {response.status_code}]"

        # Try to get the raw response text first
        raw_content = response.text
        if CONFIG['logging']['show_prompts']:
            print(f"📄 Raw response content: {raw_content}")

        try:
            response_data = response.json()
            if CONFIG['logging']['show_prompts']:
                print(f"📦 Parsed JSON response: {response_data}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return "[JSON parsing failed]"

        # Try different possible response formats
        llm_response = None

        # Format 1: {"response": "text"}
        if "response" in response_data:
            llm_response = response_data["response"]
        # Format 2: {"generated_text": "text"}
        elif "generated_text" in response_data:
            llm_response = response_data["generated_text"]
        # Format 3: {"text": "text"}
        elif "text" in response_data:
            llm_response = response_data["text"]
        # Format 4: {"output": "text"}
        elif "output" in response_data:
            llm_response = response_data["output"]
        # Format 5: Direct string response
        elif isinstance(response_data, str):
            llm_response = response_data
        # Format 6: List with text
        elif isinstance(response_data, list) and len(response_data) > 0:
            if isinstance(response_data[0], dict) and "generated_text" in response_data[0]:
                llm_response = response_data[0]["generated_text"]
            elif isinstance(response_data[0], str):
                llm_response = response_data[0]

        if llm_response is None:
            print(f"❌ Could not find response in any expected format")
            return "[Could not extract response]"

        llm_response = str(llm_response).strip()

        if not llm_response:
            print(f"⚠️  Warning: Empty response from local LLM")
            return "[Empty LLM response]"

        if CONFIG['logging']['show_prompts']:
            print(f"✅ Final local LLM response: {llm_response[:200]}...")
        return llm_response

    except requests.exceptions.Timeout as e:
        print(f"⏰ Local LLM server timeout: {e}")
        return "[LLM server timeout]"
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Local LLM server connection error: {e}")
        return "[LLM server connection failed]"
    except Exception as e:
        print(f"❌ Unexpected local LLM error: {e}")
        return "[LLM server failed]"


def analyze_numeric_column(column_data):
    """Analyze numeric column and return statistics"""
    try:
        unique_vals = column_data.dropna().unique()
        unique_sample = unique_vals.tolist() if len(unique_vals) <= 10 else random.sample(unique_vals.tolist(), 10)

        return {
            "type": str(column_data.dtype),
            "unique_values": int(column_data.nunique()),
            "sample_unique_values": [str(x) for x in unique_sample],
            "missing_values": int(column_data.isnull().sum()),
            "mean": float(column_data.mean()) if not pd.isna(column_data.mean()) else None,
            "std": float(column_data.std()) if not pd.isna(column_data.std()) else None,
            "min": float(column_data.min()) if not pd.isna(column_data.min()) else None,
            "max": float(column_data.max()) if not pd.isna(column_data.max()) else None
        }
    except Exception as e:
        print(f"Error in analyze_numeric_column: {e}")
        return {
            "type": str(column_data.dtype),
            "unique_values": 0,
            "sample_unique_values": [],
            "missing_values": len(column_data),
            "mean": None,
            "std": None,
            "min": None,
            "max": None
        }


def analyze_categorical_column(column_data):
    """Analyze categorical column and return statistics"""
    try:
        unique_vals = column_data.dropna().unique()
        unique_sample = unique_vals.tolist() if len(unique_vals) <= 10 else random.sample(unique_vals.tolist(), 10)

        top_value = None
        top_freq = None
        if not column_data.mode().empty:
            top_value = column_data.mode()[0]
        if not column_data.value_counts().empty:
            top_freq = int(column_data.value_counts().iloc[0])

        return {
            "type": str(column_data.dtype),
            "unique_values": int(column_data.nunique()),
            "sample_unique_values": [str(x) for x in unique_sample],
            "missing_values": int(column_data.isnull().sum()),
            "top_value": str(top_value) if top_value is not None else None,
            "top_freq": top_freq
        }
    except Exception as e:
        print(f"Error in analyze_categorical_column: {e}")
        return {
            "type": str(column_data.dtype),
            "unique_values": 0,
            "sample_unique_values": [],
            "missing_values": len(column_data),
            "top_value": None,
            "top_freq": None
        }


def analyze_column(column_data):
    """Main function to analyze any column type"""
    if hasattr(column_data, 'dtype') and column_data.dtype.kind in 'iuf':
        return analyze_numeric_column(column_data)
    else:
        return analyze_categorical_column(column_data)


def detect_column_type(series: pd.Series) -> str:
    """Rule-based column type detection"""
    unique_values = series.dropna().unique()
    n_unique = len(unique_values)
    dtype = series.dtype

    # Binary check
    if n_unique == 2:
        return "binary"

    # Identifier check
    if series.name and (series.name.lower() in ['id', 'identifier'] or series.name.lower().endswith('_id')):
        return "identifier"

    # Check if all values are alphanumeric and unique (potential identifier)
    if dtype == object and n_unique == len(series):
        non_null_series = series.dropna()
        if len(non_null_series) > 0 and non_null_series.apply(lambda x: isinstance(x, str) and x.isalnum()).all():
            return "identifier"

    # Free text check
    if dtype == object:
        non_null_series = series.dropna()
        if len(non_null_series) > 0:
            avg_word_count = non_null_series.apply(lambda x: len(str(x).split()) if isinstance(x, str) else 0).mean()
            if avg_word_count > 5:
                return "free_text"

    # Continuous check
    if pd.api.types.is_numeric_dtype(series):
        if n_unique > 15:
            return "continuous"

    # Ordinal check (manual or based on known categories)
    known_ordinal = {'low', 'medium', 'high', 'bad', 'average', 'good', 'excellent', 'small', 'large'}
    if dtype == object and len(unique_values) > 0:
        if any(str(val).lower() in known_ordinal for val in unique_values if val is not None):
            return "ordinal"

    # Categorical (fallback)
    if n_unique < 15:
        return "categorical"

    return "categorical" if dtype == object else "continuous"


def query_description_generation(column_name, stats, analysed_col_type, dataset_name, dataset_description,
                                 dataset_sample_str, previous_columns, additional_context=""):
    """Query LLM for column description generation with optional additional context"""
    print(f"\n📝 === DESCRIPTION GENERATION FOR COLUMN: {column_name} ===")

    user_prompt = (
            "You are generating a metadata description for a dataset column.\n\n"
            "Your task is to write a single, natural-language sentence or short paragraph that clearly describes what this column represents in real-world terms.\n\n"
            "Instructions:\n"
            "- ONLY output the column description\n"
            "- DO NOT include column name, data type, values, statistics, or usage\n"
            "- DO NOT include any extra explanation, formatting, or commentary\n"
            "- DO NOT mention or reference sample values from the column\n"
            "- DO NOT explain how the column is used in modeling or predictions\n"
            "- DO NOT include how this column might influence decisions, outcomes, or processes\n"
            "- Focus only on the real-world meaning of the column based on the dataset context (e.g., what it represents about the entity or event)\n"
            "- Write in a clear and detailed sentence or paragraph\n"

            "Examples:\n\n"

            "Example 1:\n"
            "Dataset Name: Recruitment Records\n"
            "Dataset Description: This dataset contains information about job applicants and their screening outcomes.\n"
            "Column Name: education_level\n"
            "Column Type: categorical\n"
            "Column Stats:\n"
            "{ 'type': 'object', 'unique_values': 4, 'missing_values': 12 }\n"
            "Output:\n"
            "This column represents the highest level of formal education that each job applicant has completed, typically including categories such as high school, undergraduate degrees, and advanced academic qualifications.\n\n"

            "Example 2:\n"
            "Dataset Name: E-Commerce Transactions\n"
            "Dataset Description: Logs of online purchases made through a retail platform.\n"
            "Column Name: payment_status\n"
            "Column Type: categorical\n"
            "Column Stats:\n"
            "{ 'type': 'object', 'unique_values': 3, 'missing_values': 0 }\n"
            "Output:\n"
            "This column reflects the final payment condition associated with each transaction, indicating whether the purchase was successfully completed, left pending, or encountered an issue during processing.\n\n"

            f"Dataset Name: {dataset_name}\n"
            f"Dataset Description: {dataset_description}\n"
            f"Dataset Sample:\n{dataset_sample_str}\n\n"
            f"Previously analyzed columns (name, type, description):\n" +
            "\n".join([f"- {col['name']} ({col['type']}): {col['description']}" for col in previous_columns]) + "\n\n"
                                                                                                                f"Column to describe:\n"
                                                                                                                f"Column Name: {column_name}\n"
                                                                                                                f"Probable Column Type: {analysed_col_type}\n"
                                                                                                                f"Column Stats:\n{json.dumps(stats, indent=2, default=str)}\n\n"
    )

    # Add additional context if provided
    if additional_context.strip():
        user_prompt += f"Additional Information Regarding Dataset:\n{additional_context}\n"

    user_prompt += "Now write the real-world description of this column only. Do not included any stats or sample values from the dataset."

    print(f"About to call {CONFIG['llm']['provider'].upper()} for DESCRIPTION...")
    if CONFIG['logging']['show_prompts']:
        print("\nUser Prompt:\n", user_prompt)

    response = query_llm(user_prompt)
    print(f"\n{CONFIG['llm']['provider'].upper()} DESCRIPTION Response: {response}")

    # Handle LLM failures
    if response.startswith("[") and response.endswith("]"):
        print(f"❌ {CONFIG['llm']['provider'].upper()} call failed: {response}")
        fallback_description = f"This column represents {column_name} data in the dataset."
        print(f"🔄 Using fallback description: {fallback_description}")
        return fallback_description

    return response.strip()


def query_type_classification(column_name, col_description, stats, analysed_col_type, dataset_name, dataset_description,
                              dataset_sample_str, additional_context=""):
    """Query LLM for column type classification with confidence scores and optional additional context"""
    print(f"\n🎯 === TYPE CLASSIFICATION FOR COLUMN: {column_name} ===")
    print(f"📄 Using description: {col_description[:100]}...")

    user_prompt = (
        "You are analyzing tabular data columns and classifying them into semantic types.\n"
        "Possible types are: binary, categorical, ordinal, continuous, identifier, free_text.\n"
        "Respond with a JSON object where each type is a key and the value is your confidence score (0–1).\n"
        "You MUST include all keys, even if the confidence is 0.\n"
        "Do not include any explanation.\n\n"

        "Example 1 (Binary):\n"
        "Column Name: gender\n"
        "Column Description: This column represents the biological sex of individuals\n"
        "Stats:\n"
        "{ 'type': 'object', 'unique_values': 2, 'sample_unique_values': ['Male', 'Female'], 'missing_values': 0 }\n"
        "Output:\n"
        "{\n  \"binary\": 1.0,\n  \"categorical\": 0.8,\n  \"ordinal\": 0.0,\n  \"continuous\": 0.0,\n  \"identifier\": 0.0,\n  \"free_text\": 0.0\n}\n\n"

        "Example 2 (Categorical):\n"
        "Column Name: payment_method\n"
        "Column Description: This column represents the method used to complete payment for transactions\n"
        "Stats:\n"
        "{ 'type': 'object', 'unique_values': 4, 'sample_unique_values': ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash'], 'missing_values': 5 }\n"
        "Output:\n"
        "{\n  \"binary\": 0.0,\n  \"categorical\": 1.0,\n  \"ordinal\": 0.0,\n  \"continuous\": 0.0,\n  \"identifier\": 0.0,\n  \"free_text\": 0.0\n}\n\n"

        "Example 3 (Ordinal):\n"
        "Column Name: satisfaction_level\n"
        "Column Description: This column represents customer satisfaction ratings in ordered categories\n"
        "Stats:\n"
        "{ 'type': 'object', 'unique_values': 4, 'sample_unique_values': ['Low', 'Medium', 'High', 'Very High'], 'missing_values': 3 }\n"
        "Output:\n"
        "{\n  \"binary\": 0.0,\n  \"categorical\": 0.5,\n  \"ordinal\": 1.0,\n  \"continuous\": 0.0,\n  \"identifier\": 0.0,\n  \"free_text\": 0.0\n}\n\n"

        "Example 4 (Continuous):\n"
        "Column Name: age\n"
        "Column Description: This column represents the age of individuals in years\n"
        "Stats:\n"
        "{ 'type': 'int64', 'unique_values': 43, 'mean': 36.7, 'std': 4.5, 'min': 21, 'max': 60, 'missing_values': 0 }\n"
        "Output:\n"
        "{\n  \"binary\": 0.0,\n  \"categorical\": 0.0,\n  \"ordinal\": 0.0,\n  \"continuous\": 1.0,\n  \"identifier\": 0.0,\n  \"free_text\": 0.0\n}\n\n"

        "Example 5 (Identifier):\n"
        "Column Name: CustomerId\n"
        "Column Description: This column represents unique customer identification numbers\n"
        "Stats:\n"
        "{ 'type': 'int64', 'unique_values': 10000, 'sample_unique_values': [15668009, 15732778, 15605264, 15752809], 'missing_values': 0, 'mean': 15690940.57, 'std': 71936.18, 'min': 15565701, 'max': 15815690 }\n"
        "Output:\n"
        "{\n  \"binary\": 0.0,\n  \"categorical\": 0.0,\n  \"ordinal\": 0.0,\n  \"continuous\": 0.1,\n  \"identifier\": 1.0,\n  \"free_text\": 0.0\n}\n\n"

        "Example 6 (Free Text):\n"
        "Column Name: customer_comments\n"
        "Column Description: This column contains open-ended customer feedback and comments about products or services\n"
        "Stats:\n"
        "{ 'type': 'object', 'unique_values': 9572, 'sample_unique_values': ['Loved the product, will buy again.', 'Service was poor and delivery was late.', 'Excellent value for money!', 'Would not recommend.'], 'missing_values': 412 }\n"
        "Output:\n"
        "{\n  \"binary\": 0.0,\n  \"categorical\": 0.0,\n  \"ordinal\": 0.0,\n  \"continuous\": 0.0,\n  \"identifier\": 0.0,\n  \"free_text\": 1.0\n}\n\n"

        "Now analyze the following column:\n"
        f"Dataset name:\n{dataset_name}\n"
        f"Dataset description:\n{dataset_description}\n"
        f"Dataset Sample (first 5 rows):\n{dataset_sample_str}\n\n"
        f"Column Name: {column_name}\n"
        f"Column description:\n{col_description}\n"
        f"Probable column type:\n{analysed_col_type}\n"
        f"Column statistics:\n{json.dumps(stats, indent=2, default=str)}\n\n"
    )

    # Add additional context if provided
    if additional_context.strip():
        user_prompt += f"Additional Information Regarding Dataset:\n{additional_context}\n"

    user_prompt += "Output:"

    print(f"About to call {CONFIG['llm']['provider'].upper()} for TYPE CLASSIFICATION...")
    if CONFIG['logging']['show_prompts']:
        print("\nUser Prompt:\n" + user_prompt)

    response = query_llm(user_prompt)
    print(f"\n{CONFIG['llm']['provider'].upper()} TYPE Response: {response}")

    # Handle LLM failures
    if response.startswith("[") and response.endswith("]"):
        print(f"❌ {CONFIG['llm']['provider'].upper()} call failed: {response}")
        fallback_confidence = {
            "binary": 0.0, "categorical": 0.0, "ordinal": 0.0,
            "continuous": 0.0, "identifier": 0.0, "free_text": 0.0
        }
        fallback_confidence[analysed_col_type] = 0.9
        confidence_dict = fallback_confidence
        top_type = analysed_col_type
        print(f"🔄 Using fallback type: {top_type}")
    else:
        # Parse LLM response
        try:
            confidence_dict = json.loads(response.strip())

            # Ensure all expected keys are present
            expected_keys = ["binary", "categorical", "ordinal", "continuous", "identifier", "free_text"]
            for key in expected_keys:
                confidence_dict.setdefault(key, 0.0)

            top_type = max(confidence_dict, key=confidence_dict.get)
            print(f"✅ Successfully parsed confidence scores. Top type: {top_type}")

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📄 Raw response was: {response}")
            # Fallback confidence scores
            fallback_confidence = {
                "binary": 0.0, "categorical": 0.0, "ordinal": 0.0,
                "continuous": 0.0, "identifier": 0.0, "free_text": 0.0
            }
            fallback_confidence[analysed_col_type] = 0.9
            confidence_dict = fallback_confidence
            top_type = analysed_col_type

    return {
        'confidence': confidence_dict,
        'suggested_type': top_type
    }


def make_json_serializable(obj):
    """Convert numpy types to JSON-serializable types"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj


def save_metadata(dataset_name, dataset_description, column_descriptions):
    """Save metadata to JSON file"""
    output = {
        "dataset_name": dataset_name,
        "dataset_description": dataset_description,
        "columns": [
            {k: make_json_serializable(v) for k, v in col.items()}
            for col in column_descriptions
        ]
    }

    filename = f"{dataset_name.replace(' ', '_').lower()}_metadata.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=4)

    print(f"\nMetadata saved to '{filename}'")


def get_config_info():
    """Get current configuration information"""
    provider = CONFIG['llm']['provider']
    if provider == 'openai':
        model = CONFIG['llm']['openai']['model']
        return f"OpenAI ({model})"
    elif provider == 'local':
        url = CONFIG['llm']['local']['api_url']
        return f"Local LLM ({url})"
    else:
        return f"Unknown ({provider})"


if __name__ == "__main__":
    # Test LLM connection
    if len(sys.argv) > 1 and sys.argv[1] in ["--test-llm", "--test-openai", "--test-local"]:
        test_llm_connection()
        exit(0)

    # Show configuration
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        print("=" * 60)
        print("Current Configuration:")
        print("=" * 60)
        print(f"LLM Provider: {CONFIG['llm']['provider']}")
        print(f"Configuration: {get_config_info()}")
        if CONFIG['llm']['provider'] == 'openai':
            config = CONFIG['llm']['openai']
            print(f"  Model: {config['model']}")
            print(f"  Max Tokens: {config['max_tokens']}")
            print(f"  Temperature: {config['temperature']}")
            print(f"  API Key: {'***' + config['api_key'][-8:] if len(config['api_key']) > 8 else '***'}")
        elif CONFIG['llm']['provider'] == 'local':
            config = CONFIG['llm']['local']
            print(f"  API URL: {config['api_url']}")
            print(f"  Max Tokens: {config['max_tokens']}")
            print(f"  Temperature: {config['temperature']}")

        print(f"Debug Mode: {CONFIG['app']['debug']}")
        print(f"Show Prompts: {CONFIG['logging']['show_prompts']}")
        print("=" * 60)
        exit(0)

    # CLI mode removed - redirect to web interface
    print("=" * 60)
    print("Dataset Metadata Extraction Tool")
    print("=" * 60)
    print("⚠️  CLI mode has been removed.")
    print("Please use the web interface instead:")
    print()
    print("1. Configure your LLM provider:")
    print("   Edit config.yaml or run: python meta_data_ex_api.py --config")
    print()
    print("2. Start the web server:")
    print("   python app.py")
    print()
    print("3. Open your browser:")
    print("   http://localhost:5000")
    print()
    print("4. Upload your CSV file and follow the guided workflow")
    print("5. Optionally upload additional context files (.txt, .json, .pdf, .docx)")
    print()
    print(f"🤖 Current LLM: {get_config_info()}")
    print("=" * 60)