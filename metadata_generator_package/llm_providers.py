"""
LLM provider implementations and communication logic.

Supports both OpenAI API and local LLM servers with unified interface.
Handles connection testing, error handling, and response parsing.
"""

import os
import json
import requests

# Try to import OpenAI (optional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI library not installed. Install with: pip install openai")


def initialize_openai_client(config):
    """Initialize OpenAI client if using OpenAI provider."""
    if config['llm']['provider'] == 'openai' and OPENAI_AVAILABLE:
        try:
            api_key = config['llm']['openai']['api_key']

            # Check for placeholder key
            if api_key == 'your-openai-api-key-here':
                api_key = os.getenv('OPENAI_API_KEY')

            if api_key:
                return OpenAI(api_key=api_key)
            else:
                print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable or update config.yaml")

        except Exception as e:
            print(f"❌ Error initializing OpenAI client: {e}")
    return None


def test_llm_connection(config, openai_client=None):
    """Test if the configured LLM is working properly."""
    provider = config['llm']['provider']
    test_prompt = f"Hello, please respond with '{provider.upper()} is working correctly'."
    response = query_llm(test_prompt, config, openai_client, max_tokens=50, temperature=0.1)
    return not (response.startswith("[") and response.endswith("]"))


def query_llm(prompt, config, openai_client=None, max_tokens=None, temperature=None):
    """Universal LLM query function that routes to the configured provider."""
    provider = config['llm']['provider']

    # Use config defaults if not specified
    if max_tokens is None:
        max_tokens = config['llm'][provider]['max_tokens']
    if temperature is None:
        temperature = config['llm'][provider]['temperature']

    if config['logging']['show_prompts']:
        print(f"\n🌐 Making {provider.upper()} API call...")

    # Route to appropriate provider
    if provider == 'openai':
        return _query_openai_llm(prompt, config, openai_client, max_tokens, temperature)
    elif provider == 'local':
        return _query_local_llm(prompt, config, max_tokens, temperature)
    else:
        return f"[Error: Unknown LLM provider '{provider}']"


def _query_openai_llm(prompt, config, openai_client, max_tokens, temperature):
    """Query OpenAI API for AI responses."""
    if not OPENAI_AVAILABLE or not openai_client:
        return "[Error: OpenAI not available]"

    try:
        openai_config = config['llm']['openai']

        response = openai_client.chat.completions.create(
            model=openai_config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=openai_config['timeout']
        )

        llm_response = response.choices[0].message.content.strip()
        return llm_response if llm_response else "[Empty OpenAI response]"

    except Exception as e:
        return _handle_llm_error("OpenAI API", e)


def _query_local_llm(prompt, config, max_tokens, temperature):
    """Query local/hosted LLM server for AI responses."""
    local_config = config['llm']['local']

    try:
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = requests.post(
            local_config['api_url'],
            json=payload,
            headers=local_config.get('headers', {}),
            timeout=local_config['timeout']
        )

        if response.status_code != 200:
            return f"[HTTP Error {response.status_code}]"

        # Parse response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return "[JSON parsing failed]"

        # Extract response from various possible formats
        return _extract_response_content(response_data)

    except requests.exceptions.Timeout:
        return "[LLM server timeout]"
    except requests.exceptions.ConnectionError:
        return "[LLM server connection failed]"
    except Exception as e:
        return f"[LLM server failed: {str(e)}]"


# Private helper functions

def _handle_llm_error(provider_name, error):
    """Handle LLM provider errors with consistent formatting."""
    print(f"❌ {provider_name} error: {error}")
    return f"[{provider_name} error: {str(error)}]"


def _extract_response_content(response_data):
    """Extract response content from various local LLM response formats."""
    # Try different possible response formats
    for key in ['response', 'generated_text', 'text', 'output']:
        if key in response_data:
            result = str(response_data[key]).strip()
            return result if result else "[Empty response]"

    # Handle list responses
    if isinstance(response_data, list) and response_data:
        if isinstance(response_data[0], dict) and "generated_text" in response_data[0]:
            return str(response_data[0]["generated_text"]).strip()
        elif isinstance(response_data[0], str):
            return response_data[0].strip()

    return "[Could not extract response]"