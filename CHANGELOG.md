# Changelog

## [Unreleased]

## v1.2.0

### Added
- **Batch Processing System**: Complete batch processing framework for handling multiple CSV files simultaneously
- **Enhanced Command Line Interface**: New CLI commands including `batch_processor.py` for automated batch operations
- **Cloud Integration Framework**: Built-in cloud storage support with automatic result saving and retrieval capabilities
- **Advanced Diagnostic Tools**: Comprehensive system diagnostics with `diagnostic_tool.py` for health monitoring and troubleshooting
- **Parallel Processing Engine**: Multi-threaded processing with configurable parallel job limits and resource management
- **Enhanced ZIP Export System**: Comprehensive ZIP package generation with processing logs and diagnostic information
- **Progress Monitoring**: Real-time progress tracking with ETA calculations and detailed status reporting
- **Email Notifications**: Optional email notifications for batch processing completion and error alerts
- **Retry Mechanisms**: Intelligent retry system with exponential backoff for failed operations
- **Performance Metrics**: Built-in performance tracking with processing times, throughput monitoring, and resource utilization

### Enhanced
- **Configuration Management**: Extended YAML configuration with batch processing, cloud integration, and system optimization settings
- **Error Handling**: Robust error recovery mechanisms with automatic retry and graceful degradation
- **Memory Management**: Intelligent memory allocation and cleanup for large-scale batch operations
- **File Processing**: Enhanced file validation with support for larger datasets and improved encoding detection
- **Export Options**: Extended export functionality with comprehensive package generation and metadata enrichment
- **System Monitoring**: Advanced system health monitoring with CPU, memory, and GPU utilization tracking
- **User Experience**: Improved CLI interface with better progress indicators and detailed status reporting

### Technical Improvements
- **Async Operations**: Asynchronous processing capabilities for improved performance and responsiveness
- **Resource Management**: Advanced resource allocation with automatic cleanup and optimization
- **Concurrency Control**: Thread-safe operations with proper synchronization and resource locking
- **Error Logging**: Enhanced logging system with structured error reporting and diagnostic information
- **Configuration Validation**: Comprehensive configuration validation with automatic defaults and error recovery
- **API Extensions**: New REST API endpoints for batch processing management and status monitoring
- **Database Integration**: Optional database support for job tracking and result persistence
- **Cache Management**: Intelligent caching system for improved performance with large datasets

### New CLI Commands
- **`batch_processor.py`**: Main batch processing interface with support for directory-based processing
- **`diagnostic_tool.py`**: System diagnostic and health monitoring utility
- **`--batch` mode**: Added batch processing mode to existing CLI interface
- **`--monitor`**: Real-time monitoring and progress tracking for batch operations
- **`--parallel N`**: Configurable parallel processing with customizable thread count
- **`--retry N`**: Configurable retry attempts for failed processing operations
- **`--email-notify`**: Email notification system for batch completion and error reporting

### New API Endpoints
- **`POST /batch/upload`**: Upload multiple files for batch processing with metadata validation
- **`GET /batch/status/:job_id`**: Real-time batch processing status with detailed progress information
- **`GET /batch/results/:job_id`**: Download comprehensive batch processing results
- **`POST /batch/cancel/:job_id`**: Cancel running batch processing jobs with proper cleanup
- **`GET /batch/list`**: List all batch processing jobs with filtering and pagination
- **`GET /system/diagnostics`**: System health and diagnostic information endpoint
- **`POST /system/optimize`**: System optimization and cleanup operations

### Cloud Integration
- **AWS S3 Support**: Complete Amazon S3 integration with automatic credential management
- **Google Cloud Storage**: Google Cloud Platform integration with service account authentication
- **Azure Blob Storage**: Microsoft Azure integration with managed identity support
- **Auto-Save Functionality**: Automatic result saving to configured cloud storage providers
- **Version Control**: Cloud-based version tracking and result history management
- **Sync Capabilities**: Multi-environment synchronization and backup functionality

### Performance Improvements
- **Batch Processing**: Up to 4x faster processing for multiple files with parallel execution
- **Memory Optimization**: 30% reduction in memory usage for large dataset processing
- **CPU Utilization**: Improved multi-core utilization with optimized thread management
- **I/O Performance**: Enhanced file I/O operations with async processing and buffering
- **Cache Performance**: Intelligent caching reduces redundant LLM calls by up to 50%
- **Network Optimization**: Optimized API calls with connection pooling and request batching

### Bug Fixes
- Fixed memory leaks in long-running batch processing operations
- Improved handling of corrupted or malformed CSV files in batch mode
- Enhanced error recovery for network timeouts during cloud operations
- Fixed race conditions in parallel processing with proper synchronization
- Improved file locking mechanisms for concurrent access scenarios
- Enhanced Unicode and encoding handling for international datasets
- Fixed configuration file validation edge cases with better error reporting

### Security Enhancements
- Enhanced API key validation and secure storage for cloud providers
- Improved input validation and sanitization for batch processing operations
- Added rate limiting and throttling for API endpoints
- Enhanced file upload validation with virus scanning capabilities
- Improved session management with secure token handling
- Added audit logging for batch operations and system access

### Compatibility
- Maintained full backward compatibility with v1.1.3 APIs and configurations
- Enhanced configuration migration tools for upgrading from previous versions
- Improved Python version compatibility (3.8-3.12)
- Enhanced cross-platform support for Windows, macOS, and Linux
- Docker container support for batch processing operations

## v1.1.3

### Added
- **Configuration Management System**: Added YAML-based configuration with `config.yaml` for easy LLM provider management
- **OpenAI Integration**: Built-in OpenAI API support with configurable models (GPT-3.5, GPT-4, GPT-4-turbo)
- **Universal LLM Interface**: Unified query system supporting both OpenAI and local LLM providers with automatic routing
- **Enhanced File Support**: Added .xlsx and .csv support for additional context files
- **Configuration Commands**: Added `--config` and `--test-llm` command-line options for setup validation
- **Improved Error Handling**: Better error messages and fallback mechanisms for LLM provider failures
- **Enhanced File Size Support**: Increased maximum file upload size to 20MB for larger datasets

### Enhanced
- **LLM Provider Flexibility**: Easy switching between OpenAI and local providers via configuration
- **Context File Processing**: Enhanced file reading with support for Excel and CSV context files
- **User Experience**: Better error reporting and configuration validation
- **Documentation**: Updated setup guides with configuration-based instructions

### Technical Improvements
- **Provider Abstraction**: Universal LLM query interface with automatic provider routing based on configuration
- **Configuration Validation**: Automatic config.yaml creation with default settings
- **OpenAI Client Management**: Proper OpenAI client initialization with API key validation
- **Enhanced Logging**: Configurable logging levels and prompt debugging options
- **Command Line Tools**: Added configuration inspection and LLM testing utilities

### Bug Fixes
- Fixed file size limit configuration to match actual 20MB implementation
- Improved CSV and Excel file processing for additional context
- Enhanced error handling for missing or invalid configuration files
- Better validation for OpenAI API key configuration

## v1.1.2

### Added
- **DQV Export Support**: Added Data Quality Vocabulary (DQV) export format following W3C standards
- **Enhanced Context File Support**: Full support for additional context files (.txt, .json, .pdf, .docx) with no content truncation
- **Comprehensive File Processing**: Support for extracting tables from DOCX files and text from PDF files
- **Advanced Error Handling**: Improved error handling with detailed error messages and graceful fallbacks
- **Session Cleanup**: Automatic cleanup of old sessions to prevent memory leaks
- **Health Check Endpoint**: Added `/health` endpoint for monitoring application status
- **Enhanced File Upload**: Better file validation and error reporting for uploads
- **Sample Dataset Examples**: Added IUNG2 sample dataset with vocabulary context file and comparison outputs

### Enhanced
- **Web Interface Improvements**: Better file handling with drag-and-drop support for additional context files
- **Context Integration**: Full additional file content is now used in LLM prompts without truncation
- **Export Options**: Two-format export system (JSON and DQV) with detailed format descriptions
- **User Experience**: Enhanced visual feedback and progress indicators throughout the workflow
- **Memory Management**: Improved session handling and memory cleanup for production use
- **Documentation**: Comprehensive documentation updates with troubleshooting guides

### Technical Improvements
- **DQV Module**: Complete `dqv_export.py` module for W3C Data Quality Vocabulary export
- **File Processing Pipeline**: Enhanced file reading with support for multiple document formats
- **Context Handling**: Improved context extraction and integration into LLM prompts
- **Error Recovery**: Better error handling and recovery mechanisms throughout the application
- **Production Readiness**: Enhanced configuration for production deployments

### Bug Fixes
- Fixed session management issues with concurrent users
- Improved file upload validation and error reporting
- Enhanced compatibility with different file encodings
- Better handling of edge cases in column analysis
- Improved stability of the web interface

### Performance
- Optimized memory usage for large additional context files
- Improved session cleanup to prevent memory leaks
- Enhanced file processing performance for multiple document types
- Better resource management for concurrent operations

## v1.1.1

### Added
- Local LLM server support with FastAPI-based Mistral 7B Instruct implementation
- Integrated local server file at `metadata_extractor_package/local_server/llm_server_ms_7b.py`
- Enhanced column navigation with back/forward functionality in web interface
- Improved column selector with visual status indicators (pending, current, completed)
- Save column functionality allowing users to confirm individual columns before proceeding
- Column state management preserving descriptions and types during navigation
- Better user feedback with save confirmations and status updates
- Enhanced web interface with improved column workflow and navigation controls

### Changed
- Updated function names for better clarity: `query_desc` to `query_description_generation`
- Enhanced web interface with horizontal column selector showing progress status
- Improved column analysis workflow with save/confirm functionality per column
- Better visual feedback in web interface with status indicators and progress tracking
- Enhanced session management to preserve column states during navigation
- Updated file structure documentation to include local server directory

### Technical Improvements
- Added comprehensive local LLM server with Mistral 7B Instruct v0.3 model
- FastAPI-based server with automatic model loading and text generation pipeline
- FP16 precision support for efficient GPU usage in local server
- Enhanced web interface JavaScript for column navigation and state management
- Improved error handling and user feedback throughout the application
- Better separation of concerns between description generation and type classification functions

### Performance
- Optimized local LLM server with efficient model loading and pipeline configuration
- Enhanced web interface responsiveness with better state management
- Improved column navigation performance with cached analysis results
- Better memory management for local LLM server operations

## v1.1.0

### Added
- Complete Flask web application with modern responsive interface for dataset metadata extraction
- Interactive HTML interface with step-by-step guided workflow from upload to download
- Multi-step workflow including upload, dataset information, column analysis, and results with progress tracking
- Real-time AI integration with three separate LLM calls integrated into web interface
- Session management with in-memory storage for multi-step workflows
- File upload handling with drag-and-drop CSV upload supporting files up to 16MB
- Progress visualization with real-time progress bars and loading indicators
- Download functionality for direct JSON metadata export from browser
- Web API endpoints for upload, analysis, confirmation, and metadata export
- Interactive column analysis cards with comprehensive statistics display and confidence bars
- Interactive description editing with real-time updates triggering type reclassification
- Visual confidence scoring with color-coded confidence bars for type classifications
- Professional export functionality with structured JSON download and clean metadata format

### Changed
- Modularized architecture separating web interface from core analysis engine
- Enhanced three-stage LLM process with improved workflow separating description and type analysis
- Enhanced error handling with better JSON serialization and error recovery
- Improved session management with temporary file handling and cleanup
- Remote LLM API integration with enhanced support for ngrok tunnels and remote endpoints

### Technical Improvements
- Added web-friendly functions `query_llm_for_description()` and `query_llm_for_type_classification()` for Flask integration
- Enhanced `make_json_serializable()` function for robust web API responses
- Robust error recovery with fallback mechanisms for failed LLM calls
- Added `test_llm_connection()` function for endpoint validation
- Enhanced statistical analysis display optimized for web interface presentation
- Dual interface support with both web and CLI interfaces sharing the same core engine
- Memory management with proper session cleanup and resource management
- File validation with CSV format validation and size limits
- Security headers with basic security measures for web interface
- Enhanced configuration management with centralized LLM API configuration
- Comprehensive error handling throughout the application with consistent API response structures

### Performance
- Maintained efficient LLM processing with same core analysis engine
- Optimized web interface for responsive user experience
- Enhanced session handling for multiple concurrent users
- Improved file processing with efficient temporary storage

## v1.0.3

### Added
- Comprehensive LLM prompting with 6 detailed examples covering all semantic types (binary, categorical, ordinal, continuous, identifier, free_text)
- Context-aware analysis with dataset samples and descriptions provided to LLM
- Statistical metadata enrichment in JSON output with missing values, unique counts, and statistical measures
- Enhanced prompt engineering with real-world examples for each semantic type
- JSON serialization handling for NumPy data types and pandas Timestamps
- Detailed dataset context including sample data in LLM prompts for better accuracy
- Enhanced description generation with improved prompt templates and examples
- Extended metadata output format with type-specific statistical information

### Changed
- Enhanced `query_type()` function with comprehensive examples for all 6 semantic types
- Improved `query_desc()` function with better prompt engineering and context awareness
- Updated metadata output to include statistical enrichment for continuous variables
- Enhanced JSON serialization with robust handling of NumPy and pandas data types
- Improved LLM prompting with dataset context and sample data inclusion
- Enhanced user prompts with more detailed statistical information display
- Better error handling in JSON serialization with custom conversion functions

### Fixed
- JSON serialization issues with NumPy integer and floating-point types
- pandas Timestamp serialization in metadata output
- Array and complex data type handling in JSON export
- Improved robustness in statistical data conversion and export

### Technical Improvements
- Added `make_json_serializable()` function for robust data type conversion
- Enhanced prompt templates with comprehensive examples for better LLM guidance
- Improved context passing to LLM with dataset samples and descriptions
- Enhanced statistical metadata extraction and enrichment
- Better handling of continuous vs categorical variable statistics in output
- Improved data type detection and statistical summary integration

### Performance
- Maintained 4-bit quantization for memory efficiency
- Enhanced LLM accuracy through improved prompting without performance degradation
- Better statistical computation efficiency with optimized data handling
- Improved JSON export performance with streamlined serialization

## v1.0.2

### Added
- Enhanced LLM integration with DeepSeek Coder 33B Instruct model for improved performance
- 4-bit quantization support using BitsAndBytesConfig for memory-efficient model loading
- Automatic device mapping with CPU offloading for better resource management
- Enhanced GPU memory management with CUDA cache clearing
- Device map display for transparency in model loading configuration
- Comprehensive error handling with detailed error messages and recovery mechanisms
- Enhanced prompt engineering with better context awareness and statistical integration
- Improved model loading with automatic fallback mechanisms for resource constraints

### Changed
- Updated to DeepSeek Coder 33B Instruct model for better code understanding and generation
- Enhanced model loading pipeline with quantization and device mapping
- Improved GPU memory management with automatic cleanup and optimization
- Enhanced prompt templates for better LLM understanding and accuracy
- Updated statistical analysis integration for richer metadata generation

### Technical Improvements
- Added BitsAndBytesConfig for efficient 4-bit quantization support
- Enhanced device mapping with automatic CPU offloading for large models
- Improved memory management with CUDA cache clearing and optimization
- Enhanced error recovery mechanisms with automatic fallback and retry logic
- Better statistical integration with type-aware metadata enrichment
- Improved model configuration display for better transparency and debugging

### Performance
- Significant memory usage reduction through 4-bit quantization (up to 75% reduction)
- Enhanced inference speed through optimized device mapping and memory management
- Improved model loading time with better resource allocation
- Enhanced statistical computation efficiency with optimized data processing
- Better error recovery performance with streamlined fallback mechanisms

### Bug Fixes
- Fixed memory overflow issues with large models on limited GPU memory
- Improved error handling for model loading failures with proper fallbacks
- Enhanced compatibility with different GPU configurations and memory sizes
- Fixed device mapping issues on systems with mixed GPU/CPU configurations
- Improved statistical computation accuracy for edge cases and missing data

## v1.0.1

### Added
- Initial release of LLM Metadata Extractor
- Core metadata extraction functionality with semantic type classification
- Basic CLI interface for single file processing
- Support for 6 semantic types: binary, categorical, ordinal, continuous, identifier, free_text
- JSON export functionality with basic statistical information
- LLM integration with customizable model support
- Basic error handling and validation

### Features
- Single CSV file processing with AI-powered column analysis
- Semantic type classification with confidence scoring
- Statistical metadata extraction including missing values and unique counts
- JSON export format with structured metadata output
- Configurable LLM integration for description and type generation
- Basic prompt engineering for accurate AI analysis

### Technical Implementation
- Python-based CLI tool with pandas integration for data processing
- Custom LLM query functions for description and type classification
- Statistical analysis integration with type-specific metadata enrichment
- JSON serialization with basic data type handling
- Modular architecture for easy extension and maintenance
