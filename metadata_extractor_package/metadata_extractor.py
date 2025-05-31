import argparse
import pandas as pd
import json
import random
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
import torch

torch.cuda.empty_cache()
torch.cuda.ipc_collect()

model_id = "teknium/OpenHermes-2.5-Mistral-7B"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16 
).to("cuda:0")  # Force onto GPU

llm = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0,  
    torch_dtype=torch.float16,
    return_full_text=False
)



def annotate_dataset(dataset):
    dataset_name = input("Enter the name of the dataset: ")
    dataset_description = input("Enter a description of the dataset: ")
    return {
        "name": dataset_name,
        "description": dataset_description,
        "data": dataset
    }

def display_annotated_dataset(annotated):
    print("\nDataset Name:", annotated["name"])
    print("Description:", annotated["description"])
    print("First 5 Rows:")
    print(annotated["data"].head())

def analyze_numeric_column(column_data):
    unique_vals = column_data.dropna().unique()
    unique_sample = unique_vals.tolist() if len(unique_vals) <= 10 else random.sample(unique_vals.tolist(), 10)
    return {
        "type": str(column_data.dtype),
        "unique_values": column_data.nunique(),
        "sample_unique_values": unique_sample,
        "missing_values": column_data.isnull().sum(),
        "mean": column_data.mean(),
        "std": column_data.std(),
        "min": column_data.min(),
        "max": column_data.max()
    }

def analyze_categorical_column(column_data):
    unique_vals = column_data.dropna().unique()
    unique_sample = unique_vals.tolist() if len(unique_vals) <= 10 else random.sample(unique_vals.tolist(), 10)
    return {
        "type": str(column_data.dtype),
        "unique_values": column_data.nunique(),
        "sample_unique_values": unique_sample,
        "missing_values": column_data.isnull().sum(),
        "top_value": column_data.mode()[0] if not column_data.mode().empty else None,
        "top_freq": column_data.value_counts().iloc[0] if not column_data.value_counts().empty else None
    }

def analyze_column(column_data):
    if column_data.dtype.kind in 'iuf':
        return analyze_numeric_column(column_data)
    else:
        return analyze_categorical_column(column_data)


def query_type(column_name, stats, analysed_col_type, dataset_name, dataset_description):
    print("\nColumn Type analysis:\n")

    user_prompt = (
    "You are analyzing tabular data columns and classifying them into semantic types.\n"
    "Possible types are: binary, categorical, ordinal, continuous, identifier, free_text.\n"
    "Respond with a JSON object where each type is a key and the value is your confidence score (0–1).\n"
    "You MUST include all keys, even if the confidence is 0.\n"
    "Do not include any explanation.\n\n"

    "Example 1:\n"
    "Column Name: gender\n"
    "Stats:\n"
    "{ 'type': 'object', 'unique_values': 2, 'sample_unique_values': ['Male', 'Female'], 'missing_values': 0 }\n"
    "Output:\n"
    "{\n  \"binary\": 1.0,\n  \"categorical\": 0.8,\n  \"ordinal\": 0.0,\n  \"continuous\": 0.0,\n  \"identifier\": 0.0,\n  \"free_text\": 0.0\n}\n\n"

    "Example 2:\n"
    "Column Name: age\n"
    "Stats:\n"
    "{ 'type': 'int64', 'unique_values': 43, 'mean': 36.7, 'std': 4.5, 'min': 21, 'max': 60, 'missing_values': 0 }\n"
    "Output:\n"
    "{\n  \"binary\": 0.0,\n  \"categorical\": 0.0,\n  \"ordinal\": 0.0,\n  \"continuous\": 1.0,\n  \"identifier\": 0.0,\n  \"free_text\": 0.0\n}\n\n"

    "Now analyze the following column:\n"
    f"Column Name: {column_name}\n"
    f"Dataset description:\n{dataset_description}\n"
    f"Column statistics:\n{json.dumps(stats, indent=2, default=str)}\n\n"
    "Output:"
)

    #print("Prompt: ", user_prompt)
    response = llm(user_prompt, max_new_tokens=256, do_sample=False, return_full_text=False)[0]["generated_text"].strip()

    #print("Full Response: ", response)
    trimmed_response = response.strip()
    print(f"[LLM Response]\n{trimmed_response}")

    return parse_type_from_llm_response(trimmed_response, column_name)


def parse_type_from_llm_response(response_text, column_name):
    try:
        confidence_dict = json.loads(response_text)

        # Ensure all expected keys are present
        expected_keys = ["binary", "categorical", "ordinal", "continuous", "identifier", "free_text"]
        for key in expected_keys:
            confidence_dict.setdefault(key, 0.0)

        top_type = max(confidence_dict, key=confidence_dict.get)
        top_conf = confidence_dict[top_type]

        print(f"\nThe model suggests the column is '{top_type}' with confidence {top_conf:.2f}.")
        user_input = input(f"Press Enter to accept or type a different type for the column '{column_name}': ").strip()
        return user_input.lower() if user_input else top_type

    except json.JSONDecodeError:
        print("⚠️ Warning: Could not parse LLM response as JSON.")
        print(f"Response text was:\n{response_text}")
        user_input = input(f"\nPlease manually enter the type for the column '{column_name}': ").strip()
        return user_input.lower()


def query_desc(column_name, stats, col_type, dataset_name, dataset_description):
    print("\nColumn Description analysis:\n")

    stats_json = json.dumps(stats, indent=2, default=str)

    user_prompt = (
        f"You are analyzing a column named '{column_name}' in a dataset titled '{dataset_name}'.\n"
        f"Dataset description: {dataset_description}\n"
        f"Column type: {col_type}\n"
        f"Column statistics: {stats_json}\n\n"
        "Based on the information above, write a concise description of the column suitable for metadata documentation.\n"
        "The description must be written in natural language and should not exceed 150 words.\n"
        "Do not include code, formatting syntax, or technical instructions—only clean natural language output."
    )

    #print("Prompt: ", user_prompt)

    try:
        result = llm(user_prompt, max_new_tokens=150, do_sample=True, temperature=0.7)
        response = result[0]["generated_text"].strip()

        print("[LLM Response]\n", response)
        return response
    except Exception as e:
        print("⚠️ LLM description generation failed:", str(e))
        return "[Failed to generate description]"



def get_column_type(column_name, stats, analysed_col_type, dataset_name, dataset_description):
    print(f"\nColumn: {column_name}")
    for stat, value in stats.items():
        print(f"{stat.capitalize().replace('_', ' ')}: {value}")

    # This will now include user confirmation internally
    col_type = query_type(column_name, stats, analysed_col_type, dataset_name, dataset_description)
    print(f"Final column type for '{column_name}': {col_type}")

    return col_type



def get_column_desc(column_name, stats, col_type, dataset_name, dataset_description):
    print(f"\nColumn: {column_name}")
    for stat, value in stats.items():
        print(f"{stat.capitalize().replace('_', ' ')}: {value}")

    llm_description = query_desc(column_name, stats, col_type, dataset_name, dataset_description)

    user_input = input(f"Press Enter to accept the description or type your own for '{column_name}': ").strip()
    description = user_input if user_input else llm_description

    return description


def detect_column_type(series: pd.Series) -> str:
    unique_values = series.dropna().unique()
    n_unique = len(unique_values)
    dtype = series.dtype
    # Binary check
    if n_unique == 2:
        return "binary"
    # Identifier check
    if series.name.lower() in ['id', 'identifier'] or series.name.lower().endswith('_id'):
        return "identifier"
    if series.apply(lambda x: isinstance(x, str) and x.isalnum()).all() and n_unique == len(series):
        return "identifier"
    # Free text
    if dtype == object and series.apply(lambda x: isinstance(x, str) and len(x.split()) > 5).mean() > 0.5:
        return "free_text"
    # Continuous
    if pd.api.types.is_numeric_dtype(series):
        if n_unique > 15:
            return "continuous"
    # Ordinal (manual or based on known categories)
    known_ordinal = {'low', 'medium', 'high', 'bad', 'average', 'good', 'excellent'}
    if dtype == object and any(val.lower() in known_ordinal for val in unique_values if isinstance(val, str)):
        return "ordinal"
    # Categorical (fallback)
    if n_unique < 15:
        return "categorical"

    return "categorical" if dtype == object else "continuous"

def save_metadata(dataset_name, dataset_description, column_descriptions):
    output = {
        "dataset_name": dataset_name,
        "dataset_description": dataset_description,
        "columns": column_descriptions
    }
    filename = f"{dataset_name.replace(' ', '_').lower()}_metadata.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=4)
    print(f"\nMetadata saved to '{filename}'")

def main(dataset):
    annotated = annotate_dataset(dataset)
    display_annotated_dataset(annotated)
    column_descriptions = []
    print("\nColumn-wise Analysis:\n")
    for column in dataset.columns:
        stats = analyze_column(dataset[column])
        analysed_col_type = detect_column_type(dataset[column])
        col_type = get_column_type(column, stats, analysed_col_type, annotated["name"], annotated["description"])
        description = get_column_desc(column, stats, col_type, annotated["name"], annotated["description"])
        column_descriptions.append({
            "name": column,
            "type": col_type,
            "description": description
        })
    save_metadata(annotated["name"], annotated["description"], column_descriptions)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Annotate a dataset with name and description.")
    parser.add_argument("--csv", type=str, help="Path to the dataset CSV file", required=True)
    args = parser.parse_args()
    try:
        dataset_input = pd.read_csv(args.csv)
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        print(f"Error: Failed to load the specified CSV file. {e}")
        exit(1)
    main(dataset_input)
