# Quick Setup Guide - v1.2.0

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

### 3. Configure Cloud Database (NEW in v1.2.0)

#### Option A: Automated Database Setup (Recommended)
```bash
python setup_database.py
```
This script will:
- Guide you through Supabase setup
- Validate your credentials
- Update your config.yaml
- Provide SQL commands to run
- Test your connection

#### Option B: Manual Database Setup
Edit `config.yaml`:
```yaml
database:
  enabled: true
  provider: "supabase"
  supabase:
    url: "https://your-project.supabase.co"
    key: "your-supabase-anon-key"
    auto_save: true
    bucket_name: "dataset-metadata"
```

### 4. Test LLM Connection
```bash
python meta_data_ex_api.py --test-llm
```

### 5. Start Web Interface
```bash
python app.py
```
Open `http://localhost:5000` in your browser

## Database Setup (Supabase)

### Step 1: Create Supabase Project
1. Go to [https://supabase.com](https://supabase.com)
2. Sign up for a free account
3. Create a new project
4. Go to **Settings** → **API**
5. Copy your **Project URL** and **anon public** key

### Step 2: Set Up Database Tables
1. Go to **SQL Editor** in your Supabase dashboard
2. Click **New Query** and paste the following SQL:

```sql
-- Create dataset_metadata table
CREATE TABLE IF NOT EXISTS dataset_metadata (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    dataset_name VARCHAR(500) NOT NULL,
    dataset_description TEXT,
    original_filename VARCHAR(500),
    zip_filename VARCHAR(500),
    column_count INTEGER DEFAULT 0,
    metadata_json JSONB,
    file_url TEXT,
    storage_path VARCHAR(500),
    file_size BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_file_id ON dataset_metadata(file_id);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_session_id ON dataset_metadata(session_id);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_created_at ON dataset_metadata(created_at);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_dataset_name ON dataset_metadata(dataset_name);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_dataset_metadata_updated_at 
    BEFORE UPDATE ON dataset_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

3. Click **Run** to execute the SQL

### Step 3: Set Up Storage Bucket
1. Go to **Storage** in your Supabase dashboard
2. Click **Create bucket**
3. Enter bucket name: `dataset-metadata`
4. Set it to **Private** (recommended)
5. Click **Create bucket**

### Step 4: Test Database Connection
```bash
python setup_database.py
```

This will validate your setup and test the connection.

## Environment Variables (Alternative Configuration)

Instead of editing `config.yaml`, you can use environment variables:

```bash
# LLM Configuration
export OPENAI_API_KEY="your-openai-api-key"
export LLM_PROVIDER="openai"

# Database Configuration
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-anon-key"

# Start the application
python app.py
```

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

### Database Test
After setup, test the cloud database integration:
1. Upload a CSV file through the web interface
2. Complete the analysis workflow
3. Check your Supabase dashboard to see saved results
4. Visit `http://localhost:5000/health` to check system status

## System Requirements

### Local LLM Server
- **GPU Memory**: 8GB+ VRAM recommended
- **System RAM**: 16GB+ recommended  
- **Storage**: 15GB free space for model download
- **CUDA**: Compatible GPU and drivers

### Cloud Database (NEW in v1.2.0)
- **Free Supabase Account**: Up to 500MB storage
- **Internet Connection**: Required for cloud features
- **Browser Support**: Modern browsers for dashboard access

### Enhanced File Support (v1.1.2+)
- **PDF Processing**: PyMuPDF for PDF text extraction
- **DOCX Processing**: python-docx for Word document processing
- **DQV Export**: rdflib for semantic web format export
- **Excel Support**: openpyxl for Excel file processing

## New Features in v1.2.0

### Cloud Database Integration
- **Automatic Saving**: Results automatically saved to Supabase
- **Result History**: Access previous analysis results
- **ZIP Package Storage**: Complete data packages stored in cloud
- **Web Dashboard**: View and manage saved datasets

### Batch Processing (Future Release)
- **Multiple File Processing**: Process multiple CSV files simultaneously
- **Progress Monitoring**: Real-time progress tracking
- **Error Recovery**: Automatic retry mechanisms

### Enhanced Export Options
- **ZIP Packages**: Comprehensive data packages with metadata
- **Cloud Storage**: Direct save to cloud database
- **Download History**: Access to previously generated results

## Production Deployment

### Basic Deployment
```bash
# Start local server with uvicorn
cd metadata_extractor_package/local_server
uvicorn llm_server_ms_7b:app --host 0.0.0.0 --port 8000

# Start web interface with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment (Optional)
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Environment Configuration for Production
```bash
# Production environment variables
export LLM_PROVIDER="openai"
export OPENAI_API_KEY="your-production-openai-key"
export SUPABASE_URL="https://your-production-project.supabase.co"
export SUPABASE_KEY="your-production-supabase-key"
export FLASK_ENV="production"
export APP_DEBUG="false"
```

## Troubleshooting

### Common Issues

#### LLM Connection Failed
- **Local Server**: Verify server running on port 8000
  ```bash
  curl http://localhost:8000/generate
  ```
- **OpenAI**: Check API key and quota limits
  ```bash
  python meta_data_ex_api.py --test-llm
  ```

#### Database Connection Failed
- **Check Credentials**: Run `python setup_database.py` to validate
- **Network Issues**: Verify internet connection and Supabase status
- **Permissions**: Ensure proper RLS policies in Supabase

#### File Upload Fails
- **File Size**: Check file size (max 20MB) and format
- **Permissions**: Verify temp directory write permissions
- **Format**: Ensure CSV files are properly formatted

#### GPU Memory Issues (Local LLM)
- **Monitor Usage**: `nvidia-smi` to check GPU memory
- **Requirements**: Ensure 8GB+ VRAM available
- **Drivers**: Update CUDA drivers if needed

#### Missing Dependencies
```bash
# Install missing packages
pip install PyMuPDF python-docx openpyxl supabase

# For local LLM server
pip install torch transformers accelerate bitsandbytes
```

### Health Checks
```bash
# Check system status
curl http://localhost:5000/health

# Test LLM connection
python meta_data_ex_api.py --test-llm

# Test database connection
python setup_database.py

# View diagnostic information
python diagnostic_tool.py
```

### Log Files
- **Application Logs**: Check console output for errors
- **Supabase Logs**: View logs in Supabase dashboard
- **Local LLM Logs**: Check server console for model loading issues

## Database Management

### Viewing Saved Results
1. **Web Interface**: Visit your deployed application
2. **Supabase Dashboard**: 
   - Go to **Table Editor** → `dataset_metadata`
   - View all saved analyses
3. **API Endpoints**:
   ```bash
   curl http://localhost:5000/cloud_datasets
   ```

### Database Maintenance
```sql
-- View storage usage
SELECT 
    COUNT(*) as total_datasets,
    SUM(file_size) as total_size_bytes,
    AVG(column_count) as avg_columns
FROM dataset_metadata;

-- Clean old results (optional)
DELETE FROM dataset_metadata 
WHERE created_at < NOW() - INTERVAL '90 days';
```

### Backup and Recovery
- **Automatic Backups**: Supabase provides automatic backups
- **Manual Export**: Use Supabase dashboard to export data
- **Local Backup**: 
  ```bash
  # Export database
  pg_dump "postgresql://..." > backup.sql
  ```

## Advanced Configuration

### Custom LLM Models
Edit `config.yaml` for different OpenAI models:
```yaml
llm:
  provider: "openai"
  openai:
    model: "gpt-4-turbo"  # or gpt-3.5-turbo
    max_tokens: 500
    temperature: 0.3
```

### Performance Tuning
```yaml
app:
  max_file_size_mb: 50     # Increase for larger files
  session_cleanup_hours: 2  # Adjust cleanup frequency

database:
  supabase:
    auto_save: false  # Disable for performance testing
```

### Security Settings
- **API Keys**: Use environment variables in production
- **Database Access**: Configure Row Level Security in Supabase
- **File Uploads**: Implement virus scanning for production

## Next Steps

1. **Start with OpenAI**: Easiest setup for immediate results
2. **Set up Database**: Enable cloud storage for result persistence
3. **Test with Sample Data**: Use provided examples in `examples/` directory
4. **Upload Your Data**: Process your own CSV files with optional context
5. **Export Results**: Download metadata in JSON, DQV, or ZIP formats
6. **Monitor Performance**: Use health checks and diagnostic tools
7. **Scale Up**: Move to production deployment when ready

## Support and Resources

- **Health Monitoring**: Use `/health` endpoint for system status
- **Documentation**: Complete API documentation in README.md
- **Examples**: Sample datasets and outputs in `examples/` directory
- **Issues**: Report bugs and feature requests on GitHub
- **Database Dashboard**: Supabase dashboard for data management

---

**Happy metadata extraction with v1.2.0!** 🚀
