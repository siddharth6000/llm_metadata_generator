# Quick Setup Guide - v1.1.0

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure LLM Endpoint
Edit the `API_URL` in `meta_data_ex_api.py`:
```python
API_URL = "https://your-llm-endpoint.com/generate"
```

### 3. Test LLM Connection
```bash
python meta_data_ex_api.py --test-llm
```

### 4. Choose Your Interface

#### Web Interface (Recommended)
```bash
python app.py
```
Open `http://localhost:5000` in your browser

#### Command Line Interface
```bash
python meta_data_ex_api.py --csv your_dataset.csv
```

## LLM Setup Options

### Option 1: ngrok Tunnel (Easiest)
1. Run your local LLM server (Ollama, vLLM, etc.)
2. Create ngrok tunnel: `ngrok http 8000`
3. Update `API_URL` with ngrok URL
4. Add `'ngrok-skip-browser-warning': 'true'` header (already included)

### Option 2: Local Server
```python
API_URL = "http://localhost:8000/generate"
```

### Option 3: Cloud API
```python
API_URL = "https://your-cloud-api.com/v1/generate"
```

## File Structure After Setup
```
├── app.py                    # Web interface
├── meta_data_ex_api.py      # Core engine and CLI
├── requirements.txt         # Dependencies
├── templates/
│   └── index.html          # Web UI template
├── your_dataset.csv        # Your data
└── output_metadata.json   # Generated metadata
```

## Test with Sample Data

### Web Interface Test
1. Start server: `python app.py`
2. Upload any CSV file
3. Follow the guided workflow
4. Download metadata JSON

### CLI Test
```bash
python meta_data_ex_api.py --csv sample_data.csv
```

## Production Deployment

### For Production Use
1. **Replace in-memory sessions** with Redis or database
2. **Add authentication** if needed
3. **Configure reverse proxy** (nginx)
4. **Set up monitoring** using `/health` endpoint
5. **Use production WSGI server** (gunicorn)

Example production command:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Common Issues

**LLM Connection Failed:**
- Check `API_URL` in `meta_data_ex_api.py`
- Test with: `python meta_data_ex_api.py --test-llm`
- Verify LLM server is running

**Web Interface Not Loading:**
- Check port 5000 is not in use
- Try different port: `app.run(port=5001)`

**File Upload Fails:**
- Check file size (max 16MB)
- Ensure file is valid CSV format
- Check file permissions

**Memory Issues:**
- Reduce file size
- Close other applications
- Use CPU-only mode if GPU memory insufficient

### Getting Help
1. Check the logs for error messages
2. Test LLM connection first
3. Try with smaller CSV files
4. Verify all dependencies installed

## Next Steps

1. **Test with your data** using the web interface
2. **Customize LLM prompts** in `meta_data_ex_api.py` if needed
3. **Export and use metadata** in your ML pipelines
4. **Integrate** with your existing workflows

Happy metadata extraction!
