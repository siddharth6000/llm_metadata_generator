# LLM Metadata Extractor v1.0.3

A Python tool that uses Large Language Models to analyze and annotate dataset columns with semantic types and descriptions. This version features enhanced prompting with comprehensive examples and improved metadata output with statistical enrichment.

## Features

- **Automated Statistical Analysis**: Computes descriptive statistics for numeric and categorical columns
- **Enhanced LLM Prompting**: Comprehensive examples for all 6 semantic types with improved accuracy
- **Context-Aware Analysis**: Uses dataset samples and context for better LLM understanding
- **Statistical Metadata Enrichment**: Extended JSON output with missing values, unique counts, and statistical measures
- **Rule-Based Type Detection**: Initial column type detection using heuristic algorithms
- **Interactive Validation**: User can accept or override LLM suggestions for column types and descriptions
- **JSON Confidence Scoring**: LLM provides confidence scores for each semantic type
- **Enhanced Error Handling**: Better JSON parsing and fallback mechanisms
- **Memory Optimization**: 4-bit quantization with BitsAndBytesConfig for efficient GPU usage
- **JSON Export**: Saves enriched dataset metadata in a structured JSON format

## Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended)
- Required Python packages (see requirements.txt)

## Usage

### Basic Command Line Usage
```bash
python meta_data_extractor.py --csv your_dataset.csv
```

### Example
```bash
python meta_data_extractor.py --csv datasets/Dataset.csv
```

For a complete working example, see the recruitment dataset analysis in `examples/` folder which demonstrates the tool's output evolution across versions.

## Documentation

- **Workflow Diagram**: See `docs/metadata_completion_flowchart.pdf` for a visual representation of the metadata extraction process
- **Process Flow**: The diagram shows the complete workflow from dataset upload to final JSON output
- **Future Features**: Documentation includes notes on planned fairness metadata capabilities

## How It Works

1. **Load Dataset**: The tool loads your CSV file using pandas
2. **Dataset Annotation**: You provide a name and description for the dataset
3. **For Each Column**:
   - Computes comprehensive statistical summaries
   - Applies rule-based initial type detection
   - Uses enhanced LLM prompting with 6 comprehensive examples
   - Provides dataset context and sample data to LLM
   - Displays LLM analysis and suggestions with confidence scores
   - Allows you to accept or override the LLM suggestion
   - Generates detailed column description using improved prompts
   - Allows you to accept or provide custom description
4. **Export Enriched Metadata**: Saves all annotations with statistical enrichment to a JSON file

For a visual overview of this process, see the workflow diagram in `docs/metadata_completion_flowchart.pdf`.

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

## Enhanced Output Format

The tool generates an enriched JSON file with this structure:
```json
{
    "dataset_name": "Customer Analysis Dataset",
    "dataset_description": "Customer demographics and behavior data",
    "columns": [
        {
            "name": "age",
            "type": "continuous",
            "description": "Customer age in years representing demographic information",
            "missing_values": 0,
            "unique_values": 45,
            "mean": 35.2,
            "std": 8.4,
            "min": 18.0,
            "max": 75.0
        },
        {
            "name": "gender",
            "type": "binary", 
            "description": "Customer gender classification for demographic analysis",
            "missing_values": 0,
            "unique_values": 2
        }
    ]
}
```

## LLM Integration

This version uses DeepSeek Coder 33B with enhanced prompting:
- **Model**: `deepseek-ai/deepseek-coder-33b-instruct`
- **Enhanced Prompting**: 6 comprehensive examples covering all semantic types
- **Context-Aware**: Includes dataset samples and context in prompts
- **Memory Optimization**: 4-bit quantization with BitsAndBytesConfig
- **GPU Management**: Automatic device mapping with CPU offloading when needed
- **Confidence Scoring**: Provides 0-1 confidence scores for each semantic type
- **JSON Structured Output**: Ensures consistent, parseable responses
- **Fallback Handling**: Graceful error handling with manual input fallback

## Interactive Workflow

1. Enter dataset name and description when prompted
2. For each column:
   - Review the displayed statistics
   - LLM analyzes column using enhanced prompts with comprehensive examples
   - LLM considers dataset context and sample data
   - Accept LLM suggestion or manually enter different type
   - LLM generates detailed column description based on improved prompting
   - Accept generated description or provide custom description
3. The tool saves all enriched metadata to a JSON file

## Supported Column Types

The tool classifies columns into 6 semantic types with comprehensive examples:
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
- bitsandbytes >= 0.39.0
- accelerate >= 0.20.0
- numpy >= 1.21.0

## Limitations

- Requires GPU with sufficient memory for optimal performance
- LLM suggestions require user validation
- Single CSV file processing only
- Model loading takes time on first run due to quantization

## Contributing

This is version 1.0.3 - enhanced with comprehensive prompting and statistical metadata enrichment. Future versions will include more sophisticated analysis capabilities.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
