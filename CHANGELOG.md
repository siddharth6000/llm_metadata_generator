# Changelog

## [Unreleased]

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
- Example output file (`examples/rec_deepseek_metadata.json`) demonstrating v1.0.2 capabilities
- Additional dataset examples for comprehensive testing and validation

### Changed
- Upgraded from OpenHermes-2.5-Mistral-7B to DeepSeek Coder 33B for better performance and accuracy
- Implemented 4-bit quantization (NF4) with double quantization for reduced memory usage
- Enhanced model loading with explicit trust_remote_code parameter for security
- Improved GPU utilization with automatic device mapping and CPU fallback
- Better model initialization feedback with device mapping information

### Fixed
- Memory optimization issues with large models through quantization
- GPU memory management with proper cache clearing
- Model loading reliability with improved device allocation
- Performance improvements through optimized quantization configuration

### Technical Improvements
- Added BitsAndBytesConfig for 4-bit quantization with FP16 compute dtype
- Implemented automatic device mapping for optimal resource utilization
- Enhanced model pipeline configuration with explicit return_full_text=False
- Improved memory management with torch.cuda.empty_cache() and ipc_collect()
- Added device mapping display for better debugging and transparency

### Performance
- Significantly reduced memory footprint through 4-bit quantization
- Improved inference speed with optimized model configuration
- Better GPU utilization with automatic device mapping
- Enhanced model loading efficiency with CPU offloading support

## v1.0.1

### Added
- Enhanced LLM integration with OpenHermes-2.5-Mistral-7B model
- Automated semantic type classification with confidence scoring system
- Rule-based initial column type detection using heuristic algorithms
- LLM-generated column descriptions with natural language output
- Interactive user validation workflow for type classification and descriptions
- GPU optimization with CUDA memory management and FP16 precision
- JSON structured output from LLM with confidence scores for each semantic type
- Enhanced error handling with JSON parsing fallbacks
- User override capability for both type classification and descriptions
- Example output file (`examples/rec_mistral_metadata.json`) demonstrating v1.0.1 capabilities
- Documentation folder with workflow diagrams and process flow charts (`docs/metadata_completion_flowchart.pdf`)
- Visual documentation of the metadata extraction workflow and future features roadmap

### Changed
- Upgraded from DeepSeek Coder 1.3B to OpenHermes-2.5-Mistral-7B due to performance limitations
- Resolved issue where DeepSeek Coder 1.3B was generating code outputs instead of natural language text
- Improved prompt engineering for more accurate semantic type classification
- Enhanced statistical analysis display with better formatting
- Upgraded model loading with explicit GPU allocation and memory optimization
- Improved user interaction flow with clearer prompts and validation steps

### Fixed
- JSON parsing errors from LLM responses with graceful fallback handling
- Memory management issues with CUDA cache clearing
- Model loading reliability with explicit device allocation
- Error handling for malformed or incomplete LLM responses

### Technical Improvements
- Added `detect_column_type()` function for rule-based initial classification
- Implemented `parse_type_from_llm_response()` for robust JSON parsing
- Enhanced `query_type()` and `query_desc()` functions with better prompt engineering
- Improved pipeline configuration with explicit device and dtype settings
- Added comprehensive docstring examples in prompts for better LLM guidance

### Performance
- Optimized for GPU inference with FP16 precision
- Reduced memory usage through better CUDA management
- Faster model loading and inference times
- More reliable model responses with structured JSON output

## v1.0.0

### Added
- Initial release of LLM Metadata Extractor
- Basic dataset metadata extraction workflow
- Integration with DeepSeek Coder 1.3B Instruct model for analysis assistance
- Interactive column annotation with user input prompts
- Automated statistical analysis for numeric and categorical columns
- JSON metadata export functionality
- Command-line interface with argparse support
- Support for CSV file processing
- Basic error handling for file loading
- Manual column type and description entry system

### Features
- Statistical summaries including mean, std, min, max for numeric data
- Frequency analysis for categorical data
- Missing value detection and reporting
- Sample unique values display for data understanding
- Custom LLM prompt functionality for analysis insights
- Structured JSON output with dataset and column metadata
