# Quick Setup Guide - v1.1.2

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Choose LLM Setup Method

#### Option A: Local LLM Server (Recommended)

**Step 1: Start Local Mistral 7B Server**
```bash
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py
```

The server will automatically download and load the Mistral 7B Instruct model on first run.

**Step 2: Configure Local Endpoint**
Ensure `meta_data_ex_api.py` uses local server:
```python
API_URL = "http://localhost:8000/generate"
```

#### Option B: Remote LLM Server

Edit the `API_URL` in `meta_data_ex_api.py`:
```python
API_URL = "https://your-llm-endpoint.com/generate"
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

## Local LLM Server Setup

### System Requirements
- **GPU Memory**: 8GB+ VRAM recommended for optimal performance
- **System RAM**: 16GB+ recommended
- **Storage**: 15GB free space for model download
- **CUDA**: Compatible GPU and drivers for optimal performance

### First Run
The local server will automatically:
1. Download Mistral 7B Instruct v0.3 model (approximately 13GB)
2. Load model with FP16 precision for efficiency
3. Configure automatic device mapping
4. Start FastAPI server on port 8000

### Server Configuration
The local server (`llm_server_ms_7b.py`) includes:
- **Model**: `mistralai/Mistral-7B-Instruct-v0.3`
- **Precision**: FP16 for memory efficiency
- **Device Mapping**: Automatic GPU/CPU allocation
- **Pipeline**: Optimized text generation with sampling
- **Endpoint**: `POST /generate` for text generation

## LLM Setup Options

### Option 1: Local Mistral Server (Recommended)
```bash
# Terminal 1: Start local server
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py

# Terminal 2: Start web interface
python app.py
```

**Benefits:**
- Complete privacy and offline operation
- No API costs or rate limits
- Consistent performance
- No internet dependency after setup

### Option 2: ngrok Tunnel
1. Run your local LLM server (Ollama, vLLM, etc.)
2. Create ngrok tunnel: `ngrok http 8000`
3. Update `API_URL` with ngrok URL
4. Header `'ngrok-skip-browser-warning': 'true'` already included

### Option 3: Cloud API
```python
API_URL = "https://your-cloud-api.com/v1/generate"
```

## File Structure After Setup
```
├── app.py                              # Web interface
├── meta_data_ex_api.py                # Core engine
├── dqv_export.py                      # DQV export module (NEW in v1.1.2)
├── requirements.txt                   # Dependencies
├── templates/
│   └── index.html                    # Web UI template
├── metadata_extractor_package/
│   ├── __init__.py                   # Version info
│   └── local_server/
│       └── llm_server_ms_7b.py     # Local LLM server
├── your_dataset.csv                  # Your data
├── additional_context.pdf            # Optional context files (NEW)
└── output_metadata.json             # Generated metadata
```

## New Features in v1.1.2

### DQV Export Support
```bash
# Export in W3C Data Quality Vocabulary format
# Available in web interface download options
```

### Enhanced Context File Support
- **Supported formats**: .txt, .json, .pdf, .docx
- **No content truncation**: Full file content used in analysis
- **Table extraction**: Automatic table extraction from DOCX files

### Additional File Processing
```bash
# Install optional dependencies for enhanced file support
pip install PyMuPDF python-docx  # PDF and DOCX support
```

## Test with Sample Data

### Using Provided Examples
```bash
# Navigate to examples directory
cd examples/

# Start local server (in separate terminal)
cd ../metadata_extractor_package/local_server
python llm_server_ms_7b.py

# Start web interface (in another terminal)
cd ../..
python app.py

# Test scenarios:
# 1. Upload IUNG2.csv only → Compare with iung2_metadata.json
# 2. Upload IUNG2.csv + "Pilot 5 vocabularies.docx" → Compare with iung2_metadata_additional.json
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

### Web Interface Test
1. Ensure local server is running on port 8000
2. Start web interface: `python app.py`
3. Navigate to `http://localhost:5000`
4. Upload any CSV file
5. **NEW**: Optionally upload additional context files (.txt, .json, .pdf, .docx)
6. Follow the guided workflow with enhanced column navigation
7. **NEW**: Download metadata in JSON or DQV format

## Production Deployment

### Local Server Production
```bash
# Start local server with uvicorn for production
cd metadata_extractor_package/local_server
uvicorn llm_server_ms_7b:app --host 0.0.0.0 --port 8000

# Start web interface with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### For Production Use
1. **Replace in-memory sessions** with Redis or database
2. **Add authentication** if needed
3. **Configure reverse proxy** (nginx) for both services
4. **Set up monitoring** using `/health` endpoint
5. **Use production WSGI/ASGI servers** (gunicorn, uvicorn)
6. **Implement proper logging** and error tracking

## Troubleshooting

### Local Server Issues

**Model Download Fails:**
- Check internet connection for initial download
- Ensure sufficient disk space (15GB+)
- Verify Hugging Face access for Mistral model
- Try clearing cache: `rm -rf ~/.cache/huggingface/`

**GPU Memory Issues:**
- Monitor GPU memory usage with `nvidia-smi`
- Ensure 8GB+ VRAM available
- Close other GPU-intensive applications
- Consider CPU-only mode if GPU insufficient

**Server Startup Fails:**
- Check port 8000 is not in use: `lsof -i :8000`
- Verify CUDA installation if using GPU
- Check Python environment and dependencies
- Review server logs for specific error messages

### Web Interface Issues

**LLM Connection Failed:**
- Verify local server is running on port 8000
- Check `API_URL` in `meta_data_ex_api.py`
- Test with: `python meta_data_ex_api.py --test-llm`
- Ensure firewall allows local connections

**Web Interface Not Loading:**
- Check port 5000 is not in use
- Try different port: `app.run(port=5001)`
- Verify Flask dependencies installed
- Check browser console for JavaScript errors

**File Upload Fails:**
- Check file size (max 16MB)
- Ensure file is valid CSV format
- Verify file permissions and encoding
- Try smaller test file first

### New in v1.1.2: Additional File Issues

**PDF Processing Fails:**
- Install PyMuPDF: `pip install PyMuPDF`
- Check PDF is not password protected
- Verify PDF file is not corrupted

**DOCX Processing Fails:**
- Install python-docx: `pip install python-docx`
- Ensure DOCX file is valid format
- Check file permissions

### Performance Issues

**Slow LLM Responses:**
- Ensure GPU is being used: check `nvidia-smi`
- Verify model loaded properly in server logs
- Consider reducing `max_tokens` parameter
- Monitor system memory usage

**Column Navigation Issues:**
- Check browser JavaScript console for errors
- Ensure session data is preserved
- Verify web interface state management
- Try refreshing browser if state corrupted

### Getting Help
1. Check server logs for detailed error messages
2. Test local LLM server independently
3. Verify all dependencies installed correctly
4. Try with smaller CSV files for testing
5. Monitor GPU/CPU usage during operation
6. **NEW**: Use `/health` endpoint to check system status

## Next Steps

1. **Start with local server** for best privacy and performance
2. **Test with sample data** to verify setup
3. **Upload your datasets** using the enhanced web interface
4. **Add context files** (.txt, .json, .pdf, .docx) for better analysis
5. **Navigate between columns** using the improved interface
6. **Export metadata** in JSON or DQV format
7. **Customize prompts** in `meta_data_ex_api.py` if needed

## Advanced Configuration

### Custom Model Configuration
Edit `llm_server_ms_7b.py` to customize:
- Model selection and loading parameters
- Generation parameters (temperature, max_tokens)
- Device mapping and memory optimization
- Server port and host configuration

### API Customization
Modify generation parameters in web interface:
- Temperature for creativity vs consistency
- Max tokens for response length
- Sampling parameters for generation quality

### DQV Export Customization
Edit `dqv_export.py` to customize:
- Namespace mappings and URIs
- Quality metrics and dimensions
- RDF serialization format options

Happy metadata extraction with enhanced v1.1.2 features!
