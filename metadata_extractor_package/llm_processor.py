"""AI-powered description generation and type classification functionality."""

import json
from llm_providers import query_llm


def query_description_generation(column_name, stats, analysed_col_type, dataset_name, dataset_description,
                                dataset_sample_str, previous_columns, config, openai_client=None, additional_context=""):
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
        "- Write in a clear and detailed sentence or paragraph\n\n"

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

    print(f"About to call {config['llm']['provider'].upper()} for DESCRIPTION...")
    if config['logging']['show_prompts']:
        print("\nUser Prompt:\n", user_prompt)

    response = query_llm(user_prompt, config, openai_client)
    print(f"\n{config['llm']['provider'].upper()} DESCRIPTION Response: {response}")

    # Handle LLM failures
    if response.startswith("[") and response.endswith("]"):
        print(f"❌ {config['llm']['provider'].upper()} call failed: {response}")
        fallback_description = f"This column represents {column_name} data in the dataset."
        print(f"🔄 Using fallback description: {fallback_description}")
        return fallback_description

    return response.strip()


def query_type_classification(column_name, col_description, stats, analysed_col_type, dataset_name, dataset_description,
                             dataset_sample_str, config, openai_client=None, additional_context=""):
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

    print(f"About to call {config['llm']['provider'].upper()} for TYPE CLASSIFICATION...")
    if config['logging']['show_prompts']:
        print("\nUser Prompt:\n" + user_prompt)

    response = query_llm(user_prompt, config, openai_client)
    print(f"\n{config['llm']['provider'].upper()} TYPE Response: {response}")

    # Handle LLM failures
    if response.startswith("[") and response.endswith("]"):
        print(f"❌ {config['llm']['provider'].upper()} call failed: {response}")
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