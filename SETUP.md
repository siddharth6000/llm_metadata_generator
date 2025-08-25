# Quick Setup Guide - v1.1.3

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure LLM Provider

#### Option A: OpenAI (Recommended)
Edit `config.yaml`:
```yaml
llm:
  provider: "openai"
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-4"
```

#### Option B: Local LLM Server
Edit `config.yaml`:
```yaml
llm:
  provider: "local"
  local:
    api_url: "http://localhost:8000/generate"
```

Then start local server:
```bash
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py
```

### 3. Test LLM Connection
```bash
python meta_data_ex_api.py --test-llm
```

### 4. Start Web Interface
```bash
python app.py
```
Open `http://localhost:5000` in your browser

## Test with Sample Data

### Using Provided Examples
```bash
# Use sample files in examples/ directory:
# - IUNG2.csv (sample dataset)
# - Pilot 5 vocabularies.docx (additional context file)
# - Compare outputs with provided example files
```

### Local Server Test
```bash
# Start local server
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py

# In another terminal, test connection
python meta_data_ex_api.py --test-llm

# Start web interface
python app.py
```

## System Requirements

### Local LLM Server
- **GPU Memory**: 8GB+ VRAM recommended
- **System RAM**: 16GB+ recommended  
- **Storage**: 15GB free space for model download
- **CUDA**: Compatible GPU and drivers

### Additional File Support (NEW in v1.1.2)
- **PDF Processing**: PyMuPDF for PDF text extraction
- **DOCX Processing**: python-docx for Word document processing
- **DQV Export**: rdflib for semantic web format export

## New Features in v1.1.3

### Configuration Management
- YAML-based configuration system with `config.yaml`
- Easy switching between OpenAI and local LLM providers
- Automatic configuration file creation with defaults

### OpenAI Integration
- Built-in OpenAI API support
- Support for GPT-3.5, GPT-4, and GPT-4-turbo models
- Automatic API key validation

### Enhanced File Support
- Added .xlsx and .csv support for additional context files
- Increased file size limit to 20MB for larger datasets

## Production Deployment

```bash
# Start local server with uvicorn
cd metadata_extractor_package/local_server
uvicorn llm_server_ms_7b:app --host 0.0.0.0 --port 8000

# Start web interface with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Common Issues
- **LLM Connection Failed**: Verify local server running on port 8000
- **File Upload Fails**: Check file size (max 16MB) and format
- **GPU Memory Issues**: Monitor with `nvidia-smi`, ensure 8GB+ available
- **PDF/DOCX Processing**: Install `PyMuPDF` and `python-docx` dependencies

### Health Check
```bash
# Check system status
curl http://localhost:5000/health
```

## Next Steps

1. Start with local server for privacy and performance
2. Test with provided sample files in examples/ directory
3. Upload your datasets with optional context files
4. Export metadata in JSON or DQV format
