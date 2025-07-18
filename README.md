# LLM Metadata Extractor v1.1.0

A comprehensive Python tool that uses Large Language Models to analyze and annotate dataset columns with semantic types and descriptions. This version features enhanced prompting with comprehensive examples, improved metadata output with statistical enrichment, and a modern web interface for interactive metadata generation.

## Features

### Web Interface
- **Modern Flask-based Web Application**: Interactive interface for dataset metadata extraction
- **Guided Multi-step Workflow**: Upload CSV files, provide dataset information, and analyze columns through an intuitive process
- **Real-time AI Analysis**: AI-powered column descriptions and type classifications with live feedback
- **Interactive Description Updates**: Edit descriptions and receive updated type classifications instantly
- **Progress Tracking**: Visual progress bars and step-by-step guidance through the analysis process
- **Professional Export**: Download metadata JSON files directly from the browser

### AI-Powered Analysis
- **Enhanced LLM Prompting**: Comprehensive examples for all 6 semantic types with improved accuracy
- **Context-Aware Analysis**: Uses dataset samples and context for better LLM understanding
- **Three-Stage LLM Process**: Description generation, type classification, and iterative refinement
- **Remote LLM Support**: Configurable remote LLM API endpoints with ngrok tunnel support

### Statistical Analysis
- **Automated Statistical Analysis**: Computes descriptive statistics for numeric and categorical columns
- **Statistical Metadata Enrichment**: Extended JSON output with missing values, unique counts, and statistical measures
- **Rule-Based Type Detection**: Initial column type detection using heuristic algorithms
- **Sample Value Display**: Shows representative values for better data understanding

### Semantic Type Classification
- **Binary**: Two distinct values (Male/Female, Yes/No, True/False)
- **Categorical**: Limited set of discrete values (Country, Product Category, Status)
- **Ordinal**: Ordered categorical values (Low/Medium/High, Star Ratings)
- **Continuous**: Numeric values with meaningful ranges (Age, Income, Temperature)
- **Identifier**: Unique identifiers (Customer ID, SKU, UUID)
- **Free Text**: Unstructured text content (Comments, Descriptions, Reviews)

### Export and Integration
- **JSON Confidence Scoring**: LLM provides confidence scores for each semantic type
- **Enhanced Error Handling**: Better JSON parsing and fallback mechanisms
- **Memory Optimization**: 4-bit quantization with BitsAndBytesConfig for efficient GPU usage
- **JSON Export**: Saves enriched dataset metadata in structured JSON format

## Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended)
- Required Python packages (see requirements.txt)

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface
Start the Flask web application:
```bash
python app.py
```

Open your browser to `http://localhost:5000`

#### Web Interface Workflow
1. **Upload CSV**: Drag and drop or browse for your dataset file
2. **Dataset Information**: Provide name and description with live data preview
3. **Column Analysis**: AI analyzes each column with interactive feedback and confidence visualization
4. **Download Results**: Export metadata JSON directly from browser

### Command Line Interface
```bash
python meta_data_ex_api.py --csv your_dataset.csv
```

#### Example
```bash
python meta_data_ex_api.py --csv datasets/Dataset.csv
```

### Test LLM Connection
```bash
python meta_data_ex_api.py --test-llm
```

## Configuration

### LLM API Setup
Configure your LLM endpoint in `meta_data_ex_api.py`:
```python
API_URL = "https://your-llm-endpoint.com/generate"
```

The tool supports local LLM servers, ngrok tunnels for remote access, and cloud LLM APIs with custom endpoints.

## How It Works

### Web Interface Workflow
1. **Upload Dataset**: Upload CSV file with automatic validation (maximum 16MB)
2. **Dataset Annotation**: Provide dataset name and description with data preview
3. **AI-Powered Column Analysis**: For each column:
   - View comprehensive statistics and sample values
   - AI generates natural language description
   - AI classifies semantic type with confidence scores
   - Edit descriptions to get updated type classifications
   - Confirm or override AI suggestions
4. **Export Results**: Download structured JSON metadata

### Command Line Workflow
1. **Load Dataset**: Tool loads your CSV file using pandas
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

## File Structure

```
├── app.py                    # Flask web application
├── meta_data_ex_api.py      # Core analysis engine and CLI interface
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html          # Web interface template
├── examples/               # Example outputs
├── docs/                  # Documentation
└── README.md             # This file
```

## API Endpoints

### Core Endpoints
- `POST /upload`: Upload CSV file and get initial analysis
- `POST /set_dataset_info`: Store dataset name and description
- `POST /analyze_column`: AI-powered column analysis with dual LLM calls
- `POST /reanalyze_type`: Update type based on edited description
- `POST /confirm_column`: Save confirmed column metadata
- `POST /get_metadata`: Retrieve complete dataset metadata
- `POST /download_metadata`: Download metadata JSON file

### Utility Endpoints
- `GET /health`: Health check and system status
- `GET /`: Serve web interface

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

## Requirements

```
Flask==3.0.0
pandas==2.1.4
numpy==1.24.3
requests==2.31.0
transformers==4.36.2
torch==2.1.2
Werkzeug==3.0.1
```

## Limitations

- File size limited to 16MB maximum for web uploads
- Requires configured LLM endpoint for AI features
- Optimal performance requires sufficient GPU memory
- Processes one CSV file at a time
- Web interface uses in-memory sessions (production deployments should use Redis or database)

## Examples

### Web Interface
1. Start the server: `python app.py`
2. Navigate to `http://localhost:5000`
3. Upload a CSV file and follow the guided workflow
4. Download your enriched metadata JSON

### Command Line
```bash
# Basic usage
python meta_data_ex_api.py --csv data/my_dataset.csv

# Test LLM connection
python meta_data_ex_api.py --test-llm
```

For a complete working example, see the recruitment dataset analysis in `examples/` folder which demonstrates the tool's output evolution across versions.

## Documentation

- **Workflow Diagram**: See `docs/metadata_completion_flowchart.pdf` for a visual representation of the metadata extraction process
- **Process Flow**: The diagram shows the complete workflow from dataset upload to final JSON output
- **Future Features**: Documentation includes notes on planned fairness metadata capabilities

## Interactive Workflow

### Command Line Usage
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

## LLM Integration

This version uses remote LLM APIs with enhanced prompting:
- **Remote API Support**: Configurable endpoints for various LLM providers
- **Enhanced Prompting**: 6 comprehensive examples covering all semantic types
- **Context-Aware**: Includes dataset samples and context in prompts
- **ngrok Support**: Compatible with tunneled local LLM servers
- **Confidence Scoring**: Provides 0-1 confidence scores for each semantic type
- **JSON Structured Output**: Ensures consistent, parseable responses
- **Fallback Handling**: Graceful error handling with manual input fallback

## Contributing

This is version 1.1.0 featuring the new web interface alongside enhanced AI analysis capabilities. Future versions will include more sophisticated analysis capabilities and improved deployment options.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
