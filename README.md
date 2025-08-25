# LLM Metadata Extractor v1.1.3

A comprehensive Python tool that uses Large Language Models to analyze and annotate dataset columns with semantic types and descriptions. This version features enhanced prompting, statistical enrichment, modern web interface, integrated local LLM server support, and **NEW** DQV export capabilities with enhanced context file support.

## Features

### NEW in v1.1.3
- **Configuration Management**: YAML-based configuration system with support for OpenAI and local LLM providers
- **OpenAI Integration**: Built-in OpenAI API support with configurable models (GPT-3.5, GPT-4, GPT-4-turbo)
- **Universal LLM Interface**: Unified system supporting both OpenAI and local LLM providers with automatic routing
- **Enhanced File Support**: Added .xlsx and .csv support for additional context files
- **Configuration Commands**: Added `--config` and `--test-llm` command-line options for setup validation
- **Increased File Limits**: Enhanced maximum file upload size to 20MB for larger datasets

### NEW in v1.1.2
- **DQV Export Support**: Export metadata in W3C Data Quality Vocabulary (DQV) format for semantic web applications
- **Enhanced Context File Support**: Upload additional context files (.txt, .json, .pdf, .docx, .xlsx, .csv) with full content integration
- **Configuration Management**: YAML-based configuration system with support for OpenAI and local LLM providers
- **OpenAI Integration**: Built-in OpenAI API support with configurable models (GPT-3.5, GPT-4, GPT-4-turbo)
- **Universal LLM Interface**: Unified system supporting both OpenAI and local LLM providers
- **Sample Dataset**: Added IUNG2.csv sample dataset with additional context file and example outputs
- **Production Enhancements**: Better session management, health monitoring, and memory cleanup

### Local LLM Server Support
- **Integrated Mistral 7B Server**: Built-in FastAPI server with Mistral 7B Instruct v0.3 model
- **Self-Contained Solution**: No external API dependencies required
- **GPU Optimization**: FP16 precision and automatic device mapping for efficient inference

### Web Interface
- **Modern Flask-based Web Application**: Interactive interface for dataset metadata extraction
- **Enhanced Column Navigation**: Navigate between columns with visual progress indicators
- **Guided Multi-step Workflow**: Upload CSV files, provide dataset information, and analyze columns
- **Real-time AI Analysis**: AI-powered column descriptions and type classifications with live feedback
- **Professional Export**: Download metadata in JSON or DQV format directly from the browser

### AI-Powered Analysis
- **Enhanced LLM Prompting**: Comprehensive examples for all 6 semantic types with improved accuracy
- **Context-Aware Analysis**: Uses dataset samples and additional context files for better understanding
- **Three-Stage LLM Process**: Description generation, type classification, and iterative refinement

### Semantic Type Classification
- **Binary**: Two distinct values (Male/Female, Yes/No, True/False)
- **Categorical**: Limited set of discrete values (Country, Product Category, Status)
- **Ordinal**: Ordered categorical values (Low/Medium/High, Star Ratings)
- **Continuous**: Numeric values with meaningful ranges (Age, Income, Temperature)
- **Identifier**: Unique identifiers (Customer ID, SKU, UUID)
- **Free Text**: Unstructured text content (Comments, Descriptions, Reviews)

## Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended for local LLM server)

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start
```bash
# Start local LLM server
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py

# Start web interface (in another terminal)
python app.py

# Open browser to http://localhost:5000
```

### Testing with Sample Data
Use the provided sample files in the `examples/` directory:
- Upload `IUNG2.csv` for basic testing
- Upload both `IUNG2.csv` and `Pilot 5 vocabularies.docx` for enhanced analysis with additional context

## File Structure

```
├── app.py                              # Flask web application
├── meta_data_ex_api.py                # Core analysis engine
├── dqv_export.py                      # DQV export module (NEW in v1.1.2)
├── requirements.txt                   # Python dependencies
├── templates/
│   └── index.html                    # Web interface template
├── metadata_extractor_package/
│   ├── __init__.py                   # Version information
│   └── local_server/
│       └── llm_server_ms_7b.py     # Local Mistral 7B server
├── examples/                         # Sample datasets and outputs (NEW in v1.1.2)
│   ├── README.md                    # Examples documentation
│   ├── IUNG2.csv                    # Sample dataset
│   ├── Pilot 5 vocabularies.docx    # Additional context file
│   ├── iung2_metadata.json          # Basic JSON output
│   ├── iung2_metadata.ttl           # Basic DQV output
│   ├── iung2_metadata_additional.json # Enhanced JSON output
│   └── iung2_metadata_additional.ttl  # Enhanced DQV output
└── README.md                        # This file
```

## API Endpoints

### Core Endpoints
- `POST /upload`: Upload CSV file and optional context files
- `POST /set_dataset_info`: Store dataset name and description
- `POST /analyze_column`: AI-powered column analysis
- `POST /download_metadata`: Download metadata in JSON or DQV format
- `GET /health`: Health check and system status

## Output Formats

### JSON Format
Standard structured metadata format for most applications:
```json
{
    "dataset_name": "Sample Dataset",
    "dataset_description": "Dataset description",
    "columns": [
        {
            "name": "age",
            "type": "continuous",
            "description": "Age in years",
            "missing_values": 0,
            "unique_values": 45,
            "mean": 35.2,
            "std": 8.4
        }
    ]
}
```

### DQV Format (NEW in v1.1.2)
W3C Data Quality Vocabulary format for semantic web applications:
```turtle
@prefix dqv: <http://www.w3.org/ns/dqv#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .

<http://example.org/dataset/sample> a dcat:Dataset ;
    dcterms:title "Sample Dataset" ;
    dqv:hasQualityMeasurement [
        a dqv:QualityMeasurement ;
        dqv:value 15
    ] .
```

## Requirements

```
Flask==3.0.0
pandas==2.1.4
numpy==1.24.3
requests==2.31.0
transformers==4.36.2
torch==2.1.2
fastapi>=0.68.0
uvicorn>=0.15.0
rdflib>=6.0.0          # NEW: For DQV export
PyMuPDF>=1.21.0        # NEW: For PDF processing
python-docx>=0.8.11    # NEW: For DOCX processing
psutil>=5.8.0          # NEW: For system monitoring
```

## Examples and Sample Data

The `examples/` directory contains sample datasets and outputs:
- **`IUNG2.csv`** - Sample dataset for testing
- **`Pilot 5 vocabularies.docx`** - Additional context file example
- **Output comparisons** showing improvement with additional context

See [`examples/README.md`](examples/README.md) for detailed usage instructions.

## Contributing

We welcome contributions! Please see our contribution guidelines for bug reports, feature requests, and code contributions.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See [SETUP.md](SETUP.md) for detailed setup instructions
- **Health Monitoring**: Use the `/health` endpoint for system status
- **Issues**: Report bugs and feature requests on GitHub

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and improvements.

---

**Happy metadata extraction with v1.1.2!** 🚀
