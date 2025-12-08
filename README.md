# LLM Metadata Generator v1.2.3

A comprehensive Python tool that uses Large Language Models to generate and analyze dataset metadata with semantic types and descriptions. This version introduces **enhanced privacy compliance** with a mandatory data privacy modal, ensuring users are fully informed about external LLM data processing before uploading sensitive information.

## Features

### NEW in v1.2.3
- **Privacy Modal**: Mandatory privacy and data protection warning modal that appears on every page load
- **Static Assets Folder**: New `/static` directory structure for CSS and JavaScript files
- **Enhanced User Consent**: Explicit consent mechanism with checkbox validation before application access
- **Clear Data Warnings**: Comprehensive information about external LLM processing and data transmission risks
- **Professional Privacy UI**: Dedicated `privacy-modal.css` and `privacy-modal.js` files for privacy compliance

### v1.2.2 Features
- **Enhanced Generation Capabilities**: Advanced AI-powered metadata generation with improved semantic analysis
- **Package Rename**: Complete migration from `llm_metadata_extractor` to `metadata_generator_package`
- **Improved Module Architecture**: Enhanced code organization with comprehensive docstrings and better error handling
- **Advanced Configuration Management**: Improved configuration validation with better placeholder detection
- **Enhanced Startup Diagnostics**: Better LLM connection testing and status reporting

### v1.2.1 Features
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
# Run the Docker container
docker run -p 5000:5000 -v $(pwd)/config.yaml:/app/config.yaml metadata-generator

# Access the application
# http://localhost:5000
```

### Manual Installation
```bash
# Install requirements
pip install -r requirements.txt

# Run the web interface
python app.py

# Or use the CLI
python meta_data_ex_api.py --file your_dataset.csv
```

### Configuration
Edit `config.yaml` to configure LLM provider, database, and system settings. See [SETUP.md](SETUP.md) for detailed configuration instructions.

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
├── static/                             # NEW in v1.2.3
│   ├── privacy-modal.css               # Privacy modal styles
│   └── privacy-modal.js                # Privacy modal logic
├── templates/
│   └── index.html                      # Web interface template
├── metadata_generator_package/
│   ├── __init__.py                     # Version information
│   └── local_server/
│       └── llm_server_ms_7b.py        # Local Mistral 7B server
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

## Output Formats

### JSON Format
Standard structured metadata format for most applications:
```json
{
    "dataset_name": "Sample Dataset",
    "dataset_description": "Dataset description",
    "generated_timestamp": "2025-12-08T10:30:00Z",
    "tool_version": "1.2.3",
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

### Static Files (NEW in v1.2.3)
- `GET /static/privacy-modal.css`: Privacy modal stylesheet
- `GET /static/privacy-modal.js`: Privacy modal JavaScript

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

**Happy metadata generation with v1.2.3!** 🚀
