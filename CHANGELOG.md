# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
