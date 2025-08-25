# LLM Metadata Extractor v1.2.1

A comprehensive Python tool that uses Large Language Models to analyze and annotate dataset columns with semantic types and descriptions. This version introduces **batch processing capabilities**, enhanced CLI interface, and cloud integration features while maintaining all existing functionality.

## Features

### NEW in v1.2.1
- **Enhanced Performance**: Improved memory management and processing speed for large datasets
- **Advanced Error Recovery**: Robust error handling with automatic retry mechanisms
- **Cloud Database Integration**: Built-in Supabase integration for automated result saving and retrieval
- **Comprehensive Export Options**: Enhanced ZIP export with complete package generation

### v1.2.0 Features
- **Batch Processing System**: Process multiple CSV files simultaneously with automated workflow
- **Enhanced Command Line Interface**: New CLI commands for batch operations and advanced configuration
- **Cloud Integration**: Built-in cloud storage support for automated result saving and retrieval
- **Advanced Export Options**: Enhanced ZIP export with comprehensive package generation
- **Diagnostic Tools**: Built-in system diagnostics and health monitoring tools
- **Performance Optimizations**: Improved memory management and processing speed for large datasets
- **Enhanced Error Recovery**: Robust error handling with automatic retry mechanisms

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

### Docker (Recommended)
```bash
# Build the Docker image
docker build -t metadata-extractor .

# Run the container
docker run -p 5000:5000 metadata-extractor

# Run with Docker Compose
docker-compose up

# Open browser to http://localhost:5000
```

**Note**: See [SETUP.md](SETUP.md) for configuration setup instructions.

## File Structure

```
├── app.py                              # Flask web application
├── meta_data_ex_api.py                 # Core analysis engine & CLI
├── config_manager.py                   # Configuration management
├── llm_providers.py                    # LLM provider implementations
├── column_analysis.py                  # Column analysis and type detection
├── llm_processor.py                    # LLM processing logic
├── file_handlers.py                    # File processing utilities
├── session_manager.py                  # Session management
├── cloud_database.py                   # Cloud database integration
├── metadata_export.py                  # Export functionality
├── dqv_export.py                       # DQV export module
├── config.yaml                         # Configuration file
├── requirements.txt                    # Python dependencies
├── templates/
│   └── index.html                      # Web interface template
├── metadata_extractor_package/
│   ├── __init__.py                     # Version information
│   └── local_server/
│       └── llm_server_ms_7b.py       # Local Mistral 7B server
├── examples/                           # Sample datasets and outputs
│   ├── README.md                      # Examples documentation
│   ├── IUNG2.csv                      # Sample dataset
│   ├── Pilot 5 vocabularies.docx      # Additional context file
│   ├── iung2_metadata.json            # Basic JSON output
│   ├── iung2_metadata.ttl             # Basic DQV output
│   ├── iung2_metadata_additional.json # Enhanced JSON output
│   └── iung2_metadata_additional.ttl  # Enhanced DQV output
└── README.md                           # This file
```

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

# Database Configuration
database:
  enabled: true
  provider: "supabase"
  supabase:
    url: "your-supabase-project-url"
    key: "your-supabase-anon-key"
    auto_save: true

# System Configuration
app:
  max_file_size_mb: 30
  debug: false
  session_cleanup_hours: 1
```

## Output Formats

### JSON Format
Standard structured metadata format for most applications:
```json
{
    "dataset_name": "Sample Dataset",
    "dataset_description": "Dataset description",
    "generated_timestamp": "2025-08-26T10:30:00Z",
    "tool_version": "1.2.1",
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

### ZIP Package Format
Complete data packages including:
- Original CSV dataset
- JSON metadata with full statistical analysis
- DQV metadata for semantic web compatibility
- Additional context files (if provided)
- Comprehensive README with column descriptions

## API Endpoints

### Core Endpoints
- `POST /upload`: Upload CSV file and optional context files
- `POST /set_dataset_info`: Store dataset name and description
- `POST /analyze_column`: AI-powered column analysis
- `POST /download_metadata`: Download metadata in JSON or DQV format
- `GET /health`: Health check and system status

### Cloud Database Endpoints
- `GET /cloud_datasets`: List saved datasets
- `GET /cloud_dataset/<file_id>`: Get specific dataset metadata
- `DELETE /cloud_dataset/<file_id>`: Delete dataset from cloud

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

**Happy metadata extraction with v1.2.1!** 🚀
