# Setup Guide

Complete setup instructions for LLM Metadata Extractor v1.2.1.

## Quick Setup

### Prerequisites
- Python 3.8+
- Docker (recommended)

### Docker Setup (Recommended)
```bash
# Clone repository
git clone https://github.com/your-username/llm-metadata-extractor.git
cd llm-metadata-extractor

# Build image
docker build -t metadata-extractor .

# Run container
docker run -p 5000:5000 metadata-extractor

# Open browser to http://localhost:5000
```

## Configuration

The application automatically creates `config.yaml` on first run with default values. Edit this file to configure your setup.

### Step 1: Configure LLM Provider

#### Option A: OpenAI (Recommended)
1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Edit `config.yaml`:
```yaml
llm:
  provider: "openai"
  openai:
    api_key: "your-openai-api-key-here"
    model: "gpt-3.5-turbo"
```

#### Option B: Local LLM Server
Edit `config.yaml`:
```yaml
llm:
  provider: "local"
  local:
    api_url: "http://localhost:8000/generate"
```

### Step 2: Configure Cloud Database (Optional)

#### Getting Supabase Credentials
1. **Create Supabase Account**
   - Go to https://supabase.com
   - Sign up for free account
   - Click "Create a new project"

2. **Get Project URL and API Key**
   - Go to **Settings** → **API** in your Supabase dashboard
   - Copy **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - Copy **anon public** key (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`)

3. **Update Configuration**
Edit `config.yaml`:
```yaml
database:
  enabled: true
  provider: "supabase"
  supabase:
    url: "https://your-project-id.supabase.co"
    key: "your-supabase-anon-key"
    auto_save: true
```

#### Database Setup
1. **Create Tables**
   - Go to **SQL Editor** in Supabase dashboard
   - Click **New Query**
   - Paste and run this SQL:
```sql
CREATE TABLE IF NOT EXISTS dataset_metadata (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    dataset_name VARCHAR(500) NOT NULL,
    dataset_description TEXT,
    original_filename VARCHAR(500),
    column_count INTEGER DEFAULT 0,
    metadata_json JSONB,
    file_url TEXT,
    storage_path VARCHAR(500),
    file_size BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dataset_metadata_file_id ON dataset_metadata(file_id);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_session_id ON dataset_metadata(session_id);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_created_at ON dataset_metadata(created_at);
CREATE INDEX IF NOT EXISTS idx_dataset_metadata_dataset_name ON dataset_metadata(dataset_name);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ language 'plpgsql';

CREATE TRIGGER update_dataset_metadata_updated_at 
    BEFORE UPDATE ON dataset_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

2. **Create Storage Bucket**
   - Go to **Storage** in Supabase dashboard
   - Click **Create bucket**
   - Enter name: `dataset-metadata`
   - Set to **Private**
   - Click **Create bucket**

## Docker Configuration

### Basic Docker
```bash
# Build and run
docker build -t metadata-extractor .
docker run -p 5000:5000 metadata-extractor
```

### Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  metadata-extractor:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./config.yaml:/app/config.yaml
```

Run with:
```bash
docker-compose up
```

## Running the Application

### Starting the Application
```bash
# With Docker (recommended)
docker run -p 5000:5000 metadata-extractor

# Or with Docker Compose
docker-compose up

# Open browser to http://localhost:5000
```

### Application Usage
1. Open http://localhost:5000 in your browser
2. Upload your CSV file
3. Optionally upload additional context files (.txt, .json, .pdf, .docx, .xlsx)
4. Enter dataset name and description
5. Review and edit AI-generated column descriptions
6. Download metadata in JSON, DQV, or ZIP format

## Configuration Reference

### Complete config.yaml Structure
```yaml
# LLM Provider Configuration
llm:
  provider: "openai"  # "openai" or "local"
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-3.5-turbo"
    max_tokens: 300
    temperature: 0.7
    timeout: 30
  local:
    api_url: "http://localhost:8000/generate"
    max_tokens: 300
    temperature: 0.7
    timeout: 30

# Application Settings
app:
  debug: false
  max_file_size_mb: 30
  session_cleanup_hours: 1

# Database Configuration (Optional)
database:
  enabled: true
  provider: "supabase"
  supabase:
    url: "https://your-project.supabase.co"
    key: "your-supabase-anon-key"
    auto_save: true
    bucket_name: "dataset-metadata"

# Logging
logging:
  level: "INFO"
  show_prompts: true
```

### OpenAI Model Options
- `gpt-3.5-turbo` (default, cost-effective)
- `gpt-4` (higher quality, more expensive)
- `gpt-4-turbo` (latest version)

### Supabase Configuration
- **Free Tier**: 500MB database, 1GB storage
- **Project URL**: Format `https://your-project-id.supabase.co`
- **API Key**: The "anon public" key from Settings → API
- **Auto-save**: Automatically saves analysis results to cloud

## Local LLM Server (Optional)

### Setting Up Local Server
```bash
# Start local LLM server
cd metadata_extractor_package/local_server
python llm_server_ms_7b.py

# Configure in config.yaml
llm:
  provider: "local"
  local:
    api_url: "http://localhost:8000/generate"
```

### Requirements for Local LLM
- GPU with 8GB+ VRAM recommended
- 16GB+ system RAM
- CUDA-compatible GPU and drivers

---

**Ready to extract metadata!** 🚀
