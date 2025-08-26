# Setup Guide

Complete setup instructions for LLM Metadata Extractor v1.2.2.

## Quick Setup

### Prerequisites
- Python 3.8+
- Docker (recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/llm-metadata-extractor.git
cd llm-metadata-extractor
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
1. **Run Database Setup Script**
```bash
python metadata_extractor_package/setup_database.py
```

2. **Manual Database Setup** (if script fails)
   - Go to your Supabase dashboard
   - Click on **SQL Editor** in the left sidebar
   - Click **New Query** and paste the following SQL:

```sql
-- Create dataset_metadata table
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

3. **Create Storage Bucket**
   - Go to **Storage** in your Supabase dashboard
   - Click **Create bucket**
   - Enter bucket name: `dataset-metadata`
   - Set it to **Private** (recommended)
   - Click **Create bucket**

## Docker Setup (Recommended)

After configuring your `config.yaml` file above, you can run the application using Docker.

### Option A: Docker Compose (Recommended)
```bash
# Build and run with docker-compose
docker-compose up --build

# Build without cache (clean build)
docker-compose build --no-cache

# Run in background
docker-compose up -d

# Stop and remove containers
docker-compose down

# Open browser to http://localhost:5000
```

### Option B: Docker Build and Run
```bash
# Build image
docker build -t metadata-extractor .

# Run container (localhost only)
docker run -p 5000:5000 metadata-extractor

# Run container (accessible from network)
docker run -p 0.0.0.0:5000:5000 metadata-extractor

# Open browser to http://localhost:5000
# For network access: http://YOUR_IP_ADDRESS:5000
```

## Local LLM Server (Optional)

### Start Local Server
```bash
python metadata_extractor_package/local_server/llm_server_ms_7b.py
```

### Configure for Local Server
Edit `config.yaml`:
```yaml
llm:
  provider: "local"
  local:
    api_url: "http://localhost:8000/generate"
```
### Requirements for Local LLM
- GPU with 8GB+ VRAM recommended
- 16GB+ system RAM
- CUDA-compatible GPU and drivers

## Supported File Types

### Main Dataset
- CSV files (.csv)

### Additional Context Files
- Text files (.txt)
- JSON files (.json) 
- PDF files (.pdf)
- Word documents (.docx)
- Excel files (.xlsx)
- Additional CSV files (.csv)

## Health Check
Visit: `http://localhost:5000/health`

## Troubleshooting

### Common Issues

#### Configuration Problems
- Check `config.yaml` exists and has valid values
- Ensure API keys are correctly set
- Verify Supabase credentials if using cloud database

#### Dependencies
```bash
pip install --upgrade -r requirements.txt
```

#### Database Connection
```bash
python metadata_extractor_package/setup_database.py
```

#### File Upload Issues
- Check file size (max 30MB)
- Verify supported file format
- Ensure sufficient disk space

---

**Ready to extract metadata!** 🚀
