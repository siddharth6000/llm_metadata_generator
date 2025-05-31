# LLM Metadata Extractor v1.0.0

A Python tool that uses Large Language Models to help analyze and annotate dataset columns with semantic types and descriptions.

## Features

- **Automated Statistical Analysis**: Computes descriptive statistics for numeric and categorical columns
- **LLM Integration**: Uses DeepSeek Coder 1.3B model for intelligent analysis assistance
- **Interactive Annotation**: Prompts user to manually enter column types and descriptions
- **JSON Export**: Saves dataset metadata in a structured JSON format
- **Command Line Interface**: Simple CLI for processing CSV datasets

## Installation

### Prerequisites
- Python 3.8+
- Required Python packages (see requirements.txt)

## Usage

### Basic Command Line Usage
```bash
python metadata_extractor.py --csv your_dataset.csv
```

### Example
```bash
python metadata_extractor.py --csv datasets/Dataset.csv
```

## How It Works

1. **Load Dataset**: The tool loads your CSV file using pandas
2. **Dataset Annotation**: You provide a name and description for the dataset
3. **Column Analysis**: For each column, the tool:
   - Computes statistical summaries (mean, std, unique values, etc.)
   - Displays the statistics to help you understand the column
   - Allows you to query the LLM with custom prompts for analysis assistance
   - Prompts you to manually enter the column type and description
4. **Export Metadata**: Saves all annotations to a JSON file

## Column Statistics

The tool automatically computes relevant statistics based on data type:

### Numeric Columns
- Data type, unique values, missing values
- Mean, standard deviation, min, max
- Sample of unique values

### Categorical Columns  
- Data type, unique values, missing values
- Most frequent value and its frequency
- Sample of unique values

## Output Format

The tool generates a JSON file with this structure:
```json
{
    "dataset_name": "Customer Analysis Dataset",
    "dataset_description": "Customer demographics and behavior data",
    "columns": [
        {
            "name": "age",
            "type": "continuous",
            "description": "Customer age in years"
        },
        {
            "name": "gender",
            "type": "categorical", 
            "description": "Customer gender (Male/Female)"
        }
    ]
}
```

## LLM Integration

This version uses the DeepSeek Coder 1.3B Instruct model to provide analysis assistance:
- **Model**: `deepseek-ai/deepseek-coder-1.3b-instruct`
- **Purpose**: Provides suggestions and insights to help with column classification
- **User Control**: LLM responses are advisory only - you manually enter final classifications

## Interactive Workflow

1. Enter dataset name and description when prompted
2. For each column:
   - Review the displayed statistics
   - Optionally enter a custom prompt to query the LLM for insights
   - Manually enter the column type (e.g., "categorical", "continuous", "identifier")
   - Manually enter a description for the column
3. The tool saves all metadata to a JSON file

## Supported Column Types

While you can enter any type, common semantic types include:
- **categorical**: Limited set of discrete values
- **continuous**: Numeric values with meaningful ranges  
- **binary**: Two distinct values (Yes/No, Male/Female, etc.)
- **ordinal**: Ordered categorical values (Low/Medium/High)
- **identifier**: Unique identifiers (IDs, keys, etc.)
- **text**: Free-form text content

## Requirements

- pandas >= 1.5.0
- transformers >= 4.30.0
- torch >= 2.0.0

## Limitations

- Requires manual input for column types and descriptions
- LLM responses are suggestions only and not automatically applied
- Basic statistical analysis (no advanced data profiling)
- Single CSV file processing only

## Contributing

This is version 1.0.0 - the initial implementation. Future versions will include enhanced automation and more sophisticated analysis capabilities.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
