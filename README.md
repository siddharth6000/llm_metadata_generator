# LLM Metadata Extractor v1.2.0

A comprehensive Python tool that uses Large Language Models to analyze and annotate dataset columns with semantic types and descriptions. This version introduces **batch processing capabilities**, enhanced CLI interface, and cloud integration features while maintaining all existing functionality.

## Features

### NEW in v1.2.0
- **Batch Processing System**: Process multiple CSV files simultaneously with automated workflow
- **Enhanced Command Line Interface**: New CLI commands for batch operations and advanced configuration
- **Cloud Integration**: Built-in cloud storage support for automated result saving and retrieval
- **Advanced Export Options**: Enhanced ZIP export with comprehensive package generation
- **Diagnostic Tools**: Built-in system diagnostics and health monitoring tools
- **Performance Optimizations**: Improved memory management and processing speed for large datasets
- **Enhanced Error Recovery**: Robust error handling with automatic retry mechanisms

### v1.1.3 Features
- **Configuration Management**: YAML-based configuration system with support for OpenAI and local LLM providers
- **OpenAI Integration**: Built-in OpenAI API support with configurable models (GPT-3.5, GPT-4, GPT-4-turbo)
- **Universal LLM Interface**: Unified system supporting both OpenAI and local LLM providers with automatic routing
- **Enhanced File Support**: Added .xlsx and .csv support for additional context files
- **Configuration Commands**: Added `--config` and `--test-llm` command-line options for setup validation
- **Increased File Limits**: Enhanced maximum file upload size to 20MB for larger datasets

### Core Features
- **DQV Export Support**: Export metadata in W3C Data Quality Vocabulary (DQV) format for semantic web applications
- **Enhanced Context File Support**: Upload additional context files (.txt, .json, .pdf, .docx, .xlsx, .csv) with full content integration
- **Local LLM Server Support**: Integrated Mistral 7B Server with FastAPI-based implementation
- **Modern Web Interface**: Interactive Flask-based web application with enhanced column navigation
- **AI-Powered Analysis**: Six semantic type classifications with comprehensive statistical enrichment

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
# Configure LLM provider
python meta_data_ex_api.py --config

# Test LLM connection
python meta_data_ex_api.py --test-llm

# Start web interface
python app.py

# Open browser to http://localhost:5000
```

### NEW: Batch Processing (v1.2.0)
```bash
# Process multiple CSV files in a directory
python batch_processor.py --input-dir ./datasets --output-dir ./results

# Process with specific configuration
python batch_processor.py --input-dir ./datasets --config custom_config.yaml --parallel 4

# Process with additional context files
python batch_processor.py --input-dir ./datasets --context-dir ./contexts --output-dir ./results
```

### Command Line Interface
```bash
# Single file processing
python meta_data_ex_api.py input.csv --output metadata.json

# With additional context file
python meta_data_ex_api.py input.csv --context additional_info.docx --output metadata.json

# Export to DQV format
python meta_data_ex_api.py input.csv --format dqv --output metadata.ttl

# Run diagnostic tools
python diagnostic_tool.py --full-check
```

### Local LLM Server
```bash
# Start local server
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py

# Start web interface (in another terminal)
python app.py
```

## File Structure

```
├── app.py                              # Flask web application
├── meta_data_ex_api.py                 # Core analysis engine & CLI
├── batch_processor.py                  # NEW: Batch processing system
├── metadata_export.py                  # Export functionality
├── dqv_export.py                       # DQV export module
├── config.yaml                         # Configuration file
├── requirements.txt                    # Python dependencies
├── templates/
│   └── index.html                     # Web interface template
├── metadata_extractor_package/
│   ├── __init__.py                    # Version information
│   └── local_server/
│       └── llm_server_ms_7b.py      # Local Mistral 7B server
├── examples/                          # Sample datasets and outputs
│   ├── README.md                     # Examples documentation
│   ├── IUNG2.csv                     # Sample dataset
│   ├── Pilot 5 vocabularies.docx     # Additional context file
│   ├── iung2_metadata.json           # Basic JSON output
│   ├── iung2_metadata.ttl            # Basic DQV output
│   ├── iung2_metadata_additional.json # Enhanced JSON output
│   └── iung2_metadata_additional.ttl  # Enhanced DQV output
└── README.md                          # This file
```

## API Endpoints

### Core Endpoints
- `POST /upload`: Upload CSV file and optional context files
- `POST /set_dataset_info`: Store dataset name and description
- `POST /analyze_column`: AI-powered column analysis
- `POST /download_metadata`: Download metadata in JSON or DQV format
- `GET /health`: Health check and system status

### NEW: Batch Processing Endpoints (v1.2.0)
- `POST /batch/upload`: Upload multiple files for batch processing
- `GET /batch/status/:job_id`: Check batch processing status
- `GET /batch/results/:job_id`: Download batch processing results
- `POST /batch/cancel/:job_id`: Cancel batch processing job

## Output Formats

### JSON Format
Standard structured metadata format for most applications:
```json
{
    "dataset_name": "Sample Dataset",
    "dataset_description": "Dataset description",
    "generated_timestamp": "2025-08-25T10:30:00Z",
    "tool_version": "1.2.0",
    "columns": [
        {
            "name": "age",
            "type": "continuous",
            "description": "Age in years",
            "missing_values": 0,
            "unique_values": 45,
            "mean": 35.2,
            "std": 8.4,
            "confidence_score": 0.95
        }
    ]
}
```

### DQV Format
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

### NEW: ZIP Package Format (Enhanced in v1.2.0)
Complete data packages including:
- Original CSV dataset
- JSON metadata with full statistical analysis
- DQV metadata for semantic web compatibility
- Additional context files (if provided)
- Comprehensive README with column descriptions
- Processing logs and diagnostic information

## Configuration

### config.yaml Structure
```yaml
# LLM Provider Configuration
llm:
  provider: "openai"  # or "local"
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-4"
  local:
    api_url: "http://localhost:8000/generate"

# NEW: Batch Processing Configuration
batch:
  max_parallel_jobs: 4
  timeout_minutes: 30
  retry_attempts: 3
  
# NEW: Cloud Integration
cloud:
  enabled: true
  provider: "auto"
  auto_save: true
  
# System Configuration
system:
  max_file_size_mb: 20
  debug_logging: false
  temp_dir: "./temp"
```

## Requirements

```
# Core Dependencies
Flask==3.0.0
pandas==2.1.4
numpy==1.24.3
requests==2.31.0

# AI/ML Framework
transformers==4.36.2
torch==2.1.2
fastapi>=0.68.0
uvicorn>=0.15.0

# Enhanced Processing (v1.2.0)
concurrent.futures>=3.1.1    # NEW: Batch processing
asyncio>=3.4.3              # NEW: Async operations
psutil>=5.8.0               # System monitoring

# File Format Support
rdflib>=6.0.0               # DQV export
PyMuPDF>=1.21.0            # PDF processing
python-docx>=0.8.11        # DOCX processing
openpyxl>=3.0.0            # Enhanced Excel support

# Configuration Management
PyYAML>=6.0                 # YAML configuration

# Optional: Cloud Integration (v1.2.0)
# boto3>=1.26.0             # AWS integration
# google-cloud-storage>=2.5.0 # Google Cloud integration
```

## Examples and Sample Data

The `examples/` directory contains sample datasets and outputs:
- **`IUNG2.csv`** - Sample dataset for testing
- **`Pilot 5 vocabularies.docx`** - Additional context file example
- **Output comparisons** showing improvement with additional context

### NEW: Batch Processing Examples (v1.2.0)
```bash
# Process entire examples directory
python batch_processor.py --input-dir examples/ --output-dir batch_results/

# Process with progress monitoring
python batch_processor.py --input-dir datasets/ --monitor --email-notify
```

See [`examples/README.md`](examples/README.md) for detailed usage instructions.

## Performance Optimizations (NEW in v1.2.0)

### Batch Processing
- **Parallel Processing**: Process multiple files simultaneously
- **Memory Management**: Intelligent memory allocation and cleanup
- **Progress Monitoring**: Real-time progress tracking and estimation
- **Error Recovery**: Automatic retry with exponential backoff

### System Monitoring
- **Resource Usage**: Monitor CPU, memory, and GPU utilization
- **Performance Metrics**: Track processing times and throughput
- **Health Checks**: Comprehensive system health validation
- **Diagnostic Tools**: Built-in troubleshooting and optimization suggestions

## Cloud Integration (NEW in v1.2.0)

### Automated Saving
- **Auto-Save**: Automatically save results to configured cloud storage
- **Version Control**: Track processing history and result versions
- **Backup**: Automatic backup of configurations and results
- **Sync**: Synchronize results across multiple environments

### Supported Providers
- **AWS S3**: Amazon Web Services integration
- **Google Cloud Storage**: Google Cloud Platform integration
- **Azure Blob**: Microsoft Azure integration
- **Local Network**: Network-attached storage support

## Contributing

We welcome contributions! Please see our contribution guidelines for bug reports, feature requests, and code contributions.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See [SETUP.md](SETUP.md) for detailed setup instructions
- **Health Monitoring**: Use the `/health` endpoint for system status
- **Batch Processing**: Use `diagnostic_tool.py` for troubleshooting batch operations
- **Issues**: Report bugs and feature requests on GitHub

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and improvements.

---

**Happy metadata extraction with v1.2.0!** 🚀
