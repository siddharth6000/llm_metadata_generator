import argparse
import pandas as pd
import json
import random
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re

# Initialize DeepSeek LLM model
model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
llm = pipeline("text-generation", model=model, tokenizer=tokenizer)

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


def query_llm():
    print("Column analysis:")
    user_prompt = input("Now enter your custom prompt for the LLM based on this analysis: ")

    # Add instruction to avoid code
    full_prompt = (
        f"{user_prompt}\n\n"
        "Please respond with the mentioned type alone in natural language. "
        "Do not include any Python or code examples. Only provide a textual value."
    )

    response = llm(full_prompt, max_new_tokens=500, do_sample=True, temperature=0.7)[0]["generated_text"]

    # Print only the part after the prompt to avoid echoing
    trimmed_response = response[len(full_prompt):].strip()
    print(f"[LLM Response]\n{trimmed_response}")
    return {}, ""


def describe_column(column_name, stats, dataset_name, dataset_description):
    print(f"Column: {column_name}")
    for stat, value in stats.items():
        print(f"{stat.capitalize().replace('_', ' ')}: {value}")


    query_llm()

    # Ask user for input
    col_type = input(f"Enter the type for the column '{column_name}': ")
    description = input(f"Enter a description for the column '{column_name}': ")
    return col_type, description

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
    print("\nColumn-wise Description:")
    for column in dataset.columns:
        stats = analyze_column(dataset[column])
        col_type, description = describe_column(column, stats, annotated["name"], annotated["description"])
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
