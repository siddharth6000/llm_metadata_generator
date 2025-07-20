# LLM Metadata Extractor v1.1.2

A comprehensive Python tool that uses Large Language Models to analyze and annotate dataset columns with semantic types and descriptions. This version features enhanced prompting with comprehensive examples, improved metadata output with statistical enrichment, modern web interface for interactive metadata generation, integrated local LLM server support, and **NEW** DQV export capabilities with enhanced context file support.

## Features

### NEW in v1.1.2
- **DQV Export Support**: Export metadata in W3C Data Quality Vocabulary (DQV) format for semantic web applications
- **Enhanced Context File Support**: Upload additional context files (.txt, .json, .pdf, .docx) with full content integration (no truncation)
- **Advanced File Processing**: Automatic table extraction from DOCX files and text extraction from PDF files
- **Improved Error Handling**: Enhanced error reporting and graceful fallback mechanisms
- **Production Enhancements**: Better session management, health monitoring, and memory cleanup

### Local LLM Server Support
- **Integrated Mistral 7B Server**: Built-in FastAPI server with Mistral 7B Instruct v0.3 model
- **Self-Contained Solution**: No external API dependencies required
- **GPU Optimization**: FP16 precision and automatic device mapping for efficient inference
- **Easy Setup**: Single command to start local LLM server

### Web Interface
- **Modern Flask-based Web Application**: Interactive interface for dataset metadata extraction
- **Enhanced Column Navigation**: Navigate back and forth between columns with visual progress indicators
- **Guided Multi-step Workflow**: Upload CSV files, provide dataset information, and analyze columns through an intuitive process
- **Real-time AI Analysis**: AI-powered column descriptions and type classifications with live feedback
- **Interactive Description Updates**: Edit descriptions and receive updated type classifications instantly
- **Progress Tracking**: Visual progress bars and step-by-step guidance through the analysis process
- **Professional Export**: Download metadata in JSON or DQV format directly from the browser

### AI-Powered Analysis
- **Enhanced LLM Prompting**: Comprehensive examples for all 6 semantic types with improved accuracy
- **Context-Aware Analysis**: Uses dataset samples and additional context files for better LLM understanding
- **Three-Stage LLM Process**: Description generation, type classification, and iterative refinement
- **Local and Remote LLM Support**: Works with integrated local server or configurable remote endpoints

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
- **JSON Export**: Standard structured metadata format for most applications
- **DQV Export**: W3C Data Quality Vocabulary format for semantic web and FAIR data principles
- **Enhanced Error Handling**: Better JSON parsing and fallback mechanisms
- **Memory Optimization**: Efficient model loading and inference
- **Production Ready**: Comprehensive logging, monitoring, and session management

## Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended for local LLM server)
- Required Python packages (see requirements.txt)

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Local LLM Server (Recommended)

#### Step 1: Start Local LLM Server
```bash
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py
```

The server will start on `http://localhost:8000` and automatically load the Mistral 7B Instruct model.

#### Step 2: Update Configuration
Ensure `meta_data_ex_api.py` points to local server:
```python
API_URL = "http://localhost:8000/generate"
```

#### Step 3: Start Web Interface
```bash
python app.py
```

Open your browser to `http://localhost:5000`

### Option 2: Remote LLM Server

#### Configure Remote Endpoint
Edit `API_URL` in `meta_data_ex_api.py`:
```python
API_URL = "https://your-remote-endpoint.com/generate"
```

#### Start Web Interface
```bash
python app.py
```

### Testing LLM Connection
```bash
python meta_data_ex_api.py --test-llm
```

## Configuration

### Local LLM Server
The integrated server uses Mistral 7B Instruct v0.3 with optimized settings:
- **Model**: `mistralai/Mistral-7B-Instruct-v0.3`
- **Precision**: FP16 for efficient GPU usage
- **Device Mapping**: Automatic GPU/CPU allocation
- **Pipeline**: Optimized text generation with sampling

### Remote LLM Setup
For remote endpoints, the tool supports:
- **Local servers**: Ollama, vLLM, Text Generation WebUI
- **Cloud APIs**: OpenAI, Anthropic, or custom endpoints
- **Tunneled servers**: ngrok or similar tunneling solutions

## How It Works

### Web Interface Workflow
1. **Start Local Server**: Launch the integrated Mistral 7B server for AI processing
2. **Upload Dataset**: Upload CSV file with automatic validation (maximum 16MB)
3. **Upload Context Files** (NEW): Optionally upload additional context files (.txt, .json, .pdf, .docx)
4. **Dataset Annotation**: Provide dataset name and description with data preview
5. **AI-Powered Column Analysis**: For each column:
   - View comprehensive statistics and sample values
   - AI generates natural language description using full context
   - AI classifies semantic type with confidence scores
   - Navigate between columns with back/forward controls
   - Edit descriptions to get updated type classifications
   - Save individual columns and track progress
   - Confirm or override AI suggestions
6. **Export Results**: Download structured metadata in JSON or DQV format

### Local Server Benefits
- **No Internet Required**: Fully offline operation after initial model download
- **Data Privacy**: All processing happens locally on your machine
- **Consistent Performance**: No rate limits or external API dependencies
- **Cost Effective**: No per-request charges for API usage

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
├── docs/                            # Documentation
└── README.md                       # This file
```

## API Endpoints

### Core Endpoints
- `POST /upload`: Upload CSV file and optional context files
- `POST /set_dataset_info`: Store dataset name and description
- `POST /analyze_column`: AI-powered column analysis with dual LLM calls
- `POST /reanalyze_type`: Update type based on edited description
- `POST /confirm_column`: Save confirmed column metadata
- `POST /get_metadata`: Retrieve complete dataset metadata
- `POST /download_metadata`: Download metadata in JSON or DQV format

### Utility Endpoints
- `GET /health`: Health check and system status
- `GET /`: Serve web interface

### Local LLM Server Endpoints
- `POST /generate`: Generate text using local Mistral 7B model

## Enhanced Output Format

### JSON Format
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

### DQV Format (NEW in v1.1.2)
Export metadata in W3C Data Quality Vocabulary format for semantic web applications:
```turtle
@prefix dqv: <http://www.w3.org/ns/dqv#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<http://example.org/dataset/customer_analysis> a dcat:Dataset ;
    dcterms:title "Customer Analysis Dataset" ;
    dcterms:description "Customer demographics and behavior data" ;
    dqv:hasQualityMeasurement [
        a dqv:QualityMeasurement ;
        dqv:isMeasurementOf <http://example.org/metrics/columnCount> ;
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
Werkzeug==3.0.1
fastapi>=0.68.0
uvicorn>=0.15.0
rdflib>=6.0.0          # NEW: For DQV export
PyMuPDF>=1.21.0        # NEW: For PDF processing
python-docx>=0.8.11    # NEW: For DOCX processing
psutil>=5.8.0          # NEW: For system monitoring
```

## Limitations

- **Local Server Requirements**: Local LLM server requires GPU with sufficient memory (8GB+ recommended)
- **File Size**: Web uploads limited to 16MB maximum for CSV files
- **Model Download**: Initial setup requires downloading Mistral 7B model (approximately 13GB)
- **Processing Speed**: Local inference speed depends on GPU capabilities
- **Single File Processing**: Processes one CSV file at a time
- **Session Storage**: Web interface uses in-memory sessions (production deployments should use Redis or database)

## Examples

### Local Setup Example
```bash
# Terminal 1: Start local LLM server
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py

# Terminal 2: Start web interface
python app.py

# Browser: Navigate to http://localhost:5000
```

### Enhanced Workflow Example (NEW in v1.1.2)
```bash
# 1. Upload your CSV dataset
# 2. Upload additional context (.pdf data dictionary, .txt documentation)
# 3. Provide dataset information
# 4. Navigate through columns with AI analysis
# 5. Export in JSON or DQV format
```

### Remote Setup Example
```bash
# Edit meta_data_ex_api.py
API_URL = "https://your-api-endpoint.com/generate"

# Test connection
python meta_data_ex_api.py --test-llm

# Start web interface
python app.py
```

## Examples and Sample Data

The `examples/` directory contains comprehensive sample datasets and outputs demonstrating the tool's capabilities:

### Sample Dataset: IUNG2
- **`IUNG2.csv`** - Representative dataset with mixed data types
- **`Pilot 5 vocabularies.docx`** - Additional context file with domain vocabularies
- **Output comparisons** showing improvement with additional context:
  - `iung2_metadata.json` vs `iung2_metadata_additional.json`
  - `iung2_metadata.ttl` vs `iung2_metadata_additional.ttl`

### Usage Examples
```bash
# Basic analysis (CSV only)
Upload: IUNG2.csv → Analyze → Export JSON/DQV

# Enhanced analysis (CSV + context)
Upload: IUNG2.csv + "Pilot 5 vocabularies.docx" → Analyze → Export enhanced JSON/DQV
```

The examples demonstrate significant quality improvements when using additional context files, with more accurate column descriptions and better semantic type classification.

For detailed examples documentation, see [`examples/README.md`](examples/README.md).

## Contributing

We welcome contributions! Please see our contribution guidelines for:
- Bug reports and feature requests
- Code contributions and pull requests
- Documentation improvements
- Example datasets and use cases

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{llm_metadata_extractor,
  title={LLM Metadata Extractor: AI-Powered Dataset Annotation Tool},
  author={LLM Metadata Extractor Team},
  version={1.1.2},
  year={2025},
  url={https://github.com/your-username/llm-metadata-extractor}
}
```

## Support

- **Documentation**: See [SETUP.md](SETUP.md) for detailed setup instructions
- **Troubleshooting**: Check the troubleshooting section in SETUP.md
- **Issues**: Report bugs and feature requests on GitHub
- **Health Monitoring**: Use the `/health` endpoint for system status

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and improvements.

---

**Happy metadata extraction with enhanced v1.1.2 features!** 🚀
