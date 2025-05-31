# LLM Metadata Extractor v1.0.1

A Python tool that uses Large Language Models to analyze and annotate dataset columns with semantic types and descriptions. This version features enhanced LLM integration with automated type classification and user validation.

## Features

- **Automated Statistical Analysis**: Computes descriptive statistics for numeric and categorical columns
- **LLM-Powered Type Classification**: Uses OpenHermes-2.5-Mistral-7B for intelligent semantic type classification
- **Rule-Based Type Detection**: Initial column type detection using heuristic algorithms
- **Interactive Validation**: User can accept or override LLM suggestions for column types and descriptions
- **JSON Confidence Scoring**: LLM provides confidence scores for each semantic type
- **Enhanced Error Handling**: Better JSON parsing and fallback mechanisms
- **GPU Optimization**: Optimized for CUDA with memory management
- **JSON Export**: Saves dataset metadata in a structured JSON format

## Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended)
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
3. **For Each Column**:
   - Computes comprehensive statistical summaries
   - Applies rule-based initial type detection
   - Uses LLM to classify semantic type with confidence scores
   - Displays LLM analysis and suggestions
   - Allows you to accept or override the LLM suggestion
   - Generates column description using LLM
   - Allows you to accept or provide custom description
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
            "description": "Customer age in years ranging from 18 to 75"
        },
        {
            "name": "gender",
            "type": "binary", 
            "description": "Customer gender with two values: Male and Female"
        }
    ]
}
```

## LLM Integration

This version uses OpenHermes-2.5-Mistral-7B for enhanced analysis:
- **Model**: `teknium/OpenHermes-2.5-Mistral-7B`
- **GPU Acceleration**: Optimized for CUDA with FP16 precision
- **Confidence Scoring**: Provides 0-1 confidence scores for each semantic type
- **JSON Structured Output**: Ensures consistent, parseable responses
- **Fallback Handling**: Graceful error handling with manual input fallback

## Interactive Workflow

1. Enter dataset name and description when prompted
2. For each column:
   - Review the displayed statistics
   - LLM analyzes column and suggests semantic type with confidence scores
   - Accept LLM suggestion or manually enter different type
   - LLM generates column description based on analysis
   - Accept generated description or provide custom description
3. The tool saves all metadata to a JSON file

## Supported Column Types

The tool classifies columns into 6 semantic types:
- **binary**: Two distinct values (Male/Female, Yes/No, True/False)
- **categorical**: Limited set of discrete values (Country, Product Category, Status)
- **ordinal**: Ordered categorical values (Low/Medium/High, Star Ratings)
- **continuous**: Numeric values with meaningful ranges (Age, Income, Temperature)
- **identifier**: Unique identifiers (Customer ID, SKU, UUID)
- **free_text**: Unstructured text content (Comments, Descriptions, Reviews)

## Requirements

- pandas >= 1.5.0
- transformers >= 4.30.0
- torch >= 2.0.0
- accelerate >= 0.20.0

## Limitations

- Requires GPU for optimal performance
- LLM suggestions require user validation
- Single CSV file processing only
- Model loading takes 30-60 seconds on first run

## Contributing

This is version 1.0.1 - enhanced with automated type classification and user validation. Future versions will include more sophisticated analysis capabilities.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
