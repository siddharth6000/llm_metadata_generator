# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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

### Technical Details
- Uses pandas for data manipulation
- Transformers library for LLM integration
- PyTorch as backend for model inference
- Simple pipeline-based text generation
- Basic data type detection (numeric vs categorical)
