"""
Main Flask application for Dataset Metadata Extraction Tool.

Handles web routes, file uploads, AI-powered column analysis,
and cloud database integration for metadata storage.
"""

import sys
from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import traceback
from datetime import datetime

# Import modular components
from config_manager import load_config, get_config_info, get_supabase_credentials, is_database_enabled, \
    is_auto_save_enabled
from llm_providers import initialize_openai_client, test_llm_connection
from column_analysis import analyze_column, detect_column_type
from llm_processor import query_description_generation, query_type_classification
from file_handlers import validate_csv_file, process_csv_file, validate_extra_file, read_extra_file, get_file_info, \
    secure_filename_with_session
from session_manager import create_session, get_session, update_dataset_metadata, store_column_analysis, \
    update_column_analysis, confirm_column, get_analysis_context, auto_confirm_all_columns
from metadata_export import export_json, export_dqv, export_zip

# Import cloud database manager
try:
    from cloud_database import CloudDatabaseManager

    CLOUD_DB_AVAILABLE = True
except ImportError:
    CLOUD_DB_AVAILABLE = False
    print("⚠️ Cloud database not available. Install with: pip install supabase")

# Global application state
LLM_CONNECTION_STATUS = {
    'is_connected': False,
    'tested_at_startup': False
}

# Initialize Flask app
app = Flask(__name__)

# Load configuration
CONFIG = load_config()
app.config['MAX_CONTENT_LENGTH'] = CONFIG['app']['max_file_size_mb'] * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize clients
openai_client = initialize_openai_client(CONFIG)
cloud_db_manager = None

if CLOUD_DB_AVAILABLE and is_database_enabled(CONFIG):
    try:
        supabase_url, supabase_key = get_supabase_credentials(CONFIG)
        if supabase_url and supabase_key:
            cloud_db_manager = CloudDatabaseManager(supabase_url, supabase_key)
            print(f"✅ Cloud database initialized")
        else:
            print("⚠️ Cloud database credentials not configured")
    except Exception as e:
        print(f"❌ Cloud database failed: {e}")


def initialize_llm_status():
    """Test LLM connection once and cache the result."""
    if not LLM_CONNECTION_STATUS['tested_at_startup']:
        print("🧪 Testing LLM connection...")
        llm_works = test_llm_connection(CONFIG, openai_client)

        LLM_CONNECTION_STATUS['is_connected'] = llm_works
        LLM_CONNECTION_STATUS['tested_at_startup'] = True

        if llm_works:
            print("✅ LLM initialized and connected")
        else:
            print("❌ LLM connection failed")

        return llm_works

    return LLM_CONNECTION_STATUS['is_connected']


def handle_error(error_msg, status_code=500):
    """Unified error handling with logging."""
    print(f"Error: {error_msg}")
    return jsonify({'error': error_msg}), status_code


def save_to_cloud(session_id, metadata, zip_path, original_filename):
    """Save dataset to cloud database with comprehensive logging."""
    if not cloud_db_manager or not session_id or not metadata or not metadata.get('columns'):
        return False

    if not os.path.exists(zip_path) or os.path.getsize(zip_path) == 0:
        return False

    try:
        print(f"💾 Saving to cloud database...")
        print(f"   Session ID: {session_id}")
        print(f"   Dataset: {metadata.get('dataset_name', 'Unknown')}")
        print(f"   Columns: {len(metadata.get('columns', []))}")

        result = cloud_db_manager.save_dataset_metadata(
            session_id=session_id,
            metadata=metadata,
            zip_file_path=zip_path,
            original_filename=original_filename
        )

        if result and result.get('success'):
            print(f"✅ Cloud save successful!")
            return True
        else:
            print(f"❌ Cloud save failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Cloud save error: {e}")
        return False


@app.route('/')
def index():
    """Serve the main application interface."""
    initialize_llm_status()
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and optional context file processing."""
    try:
        # Validate and process CSV
        csv_file = request.files.get('file')
        is_valid, error_msg = validate_csv_file(csv_file)
        if not is_valid:
            return handle_error(error_msg, 400)

        dataset, error_msg = process_csv_file(csv_file)
        if error_msg:
            return handle_error(error_msg, 400)

        # Handle optional extra file
        extra_content, extra_filename = "", ""
        extra_file = request.files.get('extra_file')

        if extra_file and extra_file.filename:
            is_valid, error_msg = validate_extra_file(extra_file)
            if not is_valid:
                return handle_error(error_msg, 400)

            extra_filename = secure_filename_with_session(extra_file.filename, "temp")
            extra_filepath = os.path.join(app.config['UPLOAD_FOLDER'], extra_filename)
            extra_file.save(extra_filepath)
            extra_content = read_extra_file(extra_filepath)
            extra_filename = extra_file.filename

            # Cleanup temporary file
            try:
                os.remove(extra_filepath)
            except:
                pass

        # Create session and return info
        session_id = create_session(dataset, extra_content, extra_filename)
        file_info = get_file_info(dataset, csv_file.filename)
        file_info['session_id'] = session_id
        file_info['cloud_db_enabled'] = cloud_db_manager is not None
        file_info['auto_save_enabled'] = is_auto_save_enabled(CONFIG)

        if extra_content:
            file_info['extra_file'] = {
                'filename': extra_filename,
                'content_length': len(extra_content),
                'content_preview': extra_content[:200] + ('...' if len(extra_content) > 200 else '')
            }

        return jsonify(file_info)

    except Exception as e:
        return handle_error(f'Error processing files: {str(e)}')


@app.route('/set_dataset_info', methods=['POST'])
def set_dataset_info():
    """Update dataset name and description in session."""
    try:
        data = request.json
        success = update_dataset_metadata(data.get('session_id'), data.get('name'), data.get('description'))
        return jsonify({'success': success}) if success else handle_error('Invalid session', 400)
    except Exception as e:
        return handle_error(str(e))


@app.route('/analyze_column', methods=['POST'])
def analyze_column_endpoint():
    """Analyze a specific column with AI-powered description and type detection."""
    try:
        data = request.json
        session_id, column_name = data.get('session_id'), data.get('column_name')

        session_data = get_session(session_id)
        if not session_data or column_name not in session_data['dataset'].columns:
            return handle_error('Invalid session or column', 400)

        # Analyze column
        column_data = session_data['dataset'][column_name]
        stats = analyze_column(column_data)
        detected_type = detect_column_type(column_data)
        context = get_analysis_context(session_id)

        # Generate AI description and type
        description = query_description_generation(
            column_name, stats, detected_type, context['dataset_name'],
            context['dataset_description'], context['dataset_sample_str'],
            context['previous_columns'], CONFIG, openai_client, context['additional_context']
        )

        type_result = query_type_classification(
            column_name, description, stats, detected_type,
            context['dataset_name'], context['dataset_description'],
            context['dataset_sample_str'], CONFIG, openai_client, context['additional_context']
        )

        result = {
            'column_name': column_name,
            'stats': stats,
            'detected_type': detected_type,
            'suggested_description': description,
            'suggested_type': type_result.get('suggested_type', detected_type),
            'type_confidence': type_result.get('confidence', {})
        }

        store_column_analysis(session_id, column_name, result)
        return jsonify(result)

    except Exception as e:
        return handle_error(str(e))


@app.route('/reanalyze_type', methods=['POST'])
def reanalyze_type():
    """Reanalyze column type based on updated description."""
    try:
        data = request.json
        session_id, column_name = data.get('session_id'), data.get('column_name')
        updated_description = data.get('description')

        session_data = get_session(session_id)
        if not session_data:
            return handle_error('Invalid session', 400)

        analysis_data = session_data.get('analysis_results', {}).get(column_name)
        if not analysis_data:
            return handle_error('Column not analyzed', 400)

        context = get_analysis_context(session_id)
        type_result = query_type_classification(
            column_name, updated_description, analysis_data['stats'],
            analysis_data['detected_type'], context['dataset_name'],
            context['dataset_description'], context['dataset_sample_str'],
            CONFIG, openai_client, context['additional_context']
        )

        update_column_analysis(session_id, column_name, {
            'description': updated_description,
            'type': type_result['suggested_type']
        })

        return jsonify({
            'column_name': column_name,
            'suggested_type': type_result['suggested_type']
        })

    except Exception as e:
        return handle_error(str(e))


@app.route('/confirm_column', methods=['POST'])
def confirm_column_endpoint():
    """Confirm final column metadata after user review."""
    try:
        data = request.json
        success = confirm_column(
            data.get('session_id'), data.get('column_name'),
            data.get('type'), data.get('description')
        )
        return jsonify({'success': success}) if success else handle_error('Failed to confirm column', 400)
    except Exception as e:
        return handle_error(str(e))


@app.route('/get_metadata', methods=['POST'])
def get_metadata():
    """Generate final metadata and optionally save to cloud."""
    try:
        session_id = request.json.get('session_id')
        session_data = get_session(session_id)
        if not session_data:
            return handle_error('Invalid session', 400)

        metadata = {
            "dataset_name": session_data['metadata'].get('dataset_name'),
            "dataset_description": session_data['metadata'].get('dataset_description'),
            "columns": session_data.get('columns_processed', [])
        }

        print(f"📊 Generated metadata for session {session_id}")

        # Auto-save to cloud database if enabled
        if cloud_db_manager and is_auto_save_enabled(CONFIG) and len(metadata.get('columns', [])) > 0:
            try:
                print("📄 Auto-save is enabled, attempting to save...")

                # Generate ZIP file
                dataset = session_data['dataset']
                zip_filepath, zip_filename = export_zip(
                    metadata, session_id, dataset,
                    session_data.get('extra_filename', ''),
                    session_data.get('extra_content', '')
                )

                # Save to cloud
                original_filename = f"{metadata.get('dataset_name', 'dataset')}.csv"
                save_success = save_to_cloud(session_id, metadata, zip_filepath, original_filename)

                # Cleanup temporary ZIP file
                try:
                    if os.path.exists(zip_filepath):
                        os.remove(zip_filepath)
                except Exception:
                    pass

                if save_success:
                    print("🎉 Auto-save completed successfully!")

            except Exception as auto_save_error:
                print(f"⚠️ Auto-save to cloud database failed: {auto_save_error}")

        return jsonify(metadata)

    except Exception as e:
        return handle_error(str(e))


@app.route('/download_metadata', methods=['POST'])
def download_metadata():
    """Download metadata in specified format (JSON, DQV, or ZIP)."""
    try:
        data = request.json
        session_id, format_type = data.get('session_id'), data.get('format', 'json')

        session_data = get_session(session_id)
        if not session_data:
            return handle_error('Invalid session', 400)

        metadata = {
            "dataset_name": session_data['metadata'].get('dataset_name', 'Unknown Dataset'),
            "dataset_description": session_data['metadata'].get('dataset_description', 'No description'),
            "columns": session_data.get('columns_processed', [])
        }

        # Export based on format
        if format_type == 'dqv':
            filepath, filename = export_dqv(metadata, session_id)
            mimetype = 'text/turtle'
        elif format_type == 'zip':
            dataset = session_data['dataset']
            filepath, filename = export_zip(
                metadata, session_id, dataset,
                session_data.get('extra_filename', ''),
                session_data.get('extra_content', '')
            )
            mimetype = 'application/zip'

            # Save to cloud if enabled
            if cloud_db_manager and is_database_enabled(CONFIG):
                try:
                    print("💾 Saving ZIP download to cloud database...")
                    original_filename = f"{metadata.get('dataset_name', 'dataset')}.csv"
                    save_to_cloud(session_id, metadata, filepath, original_filename)
                except Exception as e:
                    print(f"⚠️ ZIP download cloud save failed: {e}")
        else:
            filepath, filename = export_json(metadata, session_id)
            mimetype = 'application/json'

        if not os.path.exists(filepath):
            return handle_error('Failed to create file')

        return send_file(filepath, as_attachment=True, download_name=filename, mimetype=mimetype)

    except Exception as e:
        return handle_error(f'Download failed: {str(e)}')


@app.route('/auto_confirm_columns', methods=['POST'])
def auto_confirm_columns():
    """Auto-confirm all analyzed columns for quick completion."""
    try:
        session_id = request.json.get('session_id')
        success = auto_confirm_all_columns(session_id)

        if success:
            session_data = get_session(session_id)
            return jsonify({
                'success': True,
                'columns_confirmed': len(session_data.get('columns_processed', []))
            })
        return handle_error('Failed to auto-confirm columns')
    except Exception as e:
        return handle_error(str(e))


@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    try:
        initialize_llm_status()
        llm_status_text = 'connected' if LLM_CONNECTION_STATUS['is_connected'] else 'disconnected'

        cloud_db_status = False
        cloud_db_info = "disabled"
        if cloud_db_manager:
            try:
                usage = cloud_db_manager.get_storage_usage()
                cloud_db_status = True
                cloud_db_info = f"connected ({usage['total_files']} files, {usage['total_size_mb']} MB)"
            except Exception as e:
                cloud_db_info = f"error: {str(e)}"

        return jsonify({
            'status': 'healthy',
            'llm_status': llm_status_text,
            'llm_provider': CONFIG['llm']['provider'],
            'cloud_db_status': 'connected' if cloud_db_status else 'disconnected',
            'cloud_db_info': cloud_db_info,
            'auto_save_enabled': is_auto_save_enabled(CONFIG),
            'version': '2.1.0'
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check that tests LLM connection fresh."""
    try:
        llm_status = test_llm_connection(CONFIG, openai_client)

        cloud_db_status = False
        cloud_db_info = "disabled"
        if cloud_db_manager:
            try:
                usage = cloud_db_manager.get_storage_usage()
                cloud_db_status = True
                cloud_db_info = f"connected ({usage['total_files']} files, {usage['total_size_mb']} MB)"
            except Exception as e:
                cloud_db_info = f"error: {str(e)}"

        return jsonify({
            'status': 'healthy',
            'llm_status': 'connected' if llm_status else 'disconnected',
            'llm_provider': CONFIG['llm']['provider'],
            'cloud_db_status': 'connected' if cloud_db_status else 'disconnected',
            'cloud_db_info': cloud_db_info,
            'auto_save_enabled': is_auto_save_enabled(CONFIG),
            'version': '2.1.0',
            'note': 'Fresh LLM connectivity test performed'
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


# Cloud database routes (if enabled)
@app.route('/cloud_datasets', methods=['GET'])
def get_cloud_datasets():
    """Get list of datasets from cloud database."""
    if not cloud_db_manager:
        return handle_error('Cloud database not available', 400)

    try:
        limit = request.args.get('limit', 50, type=int)
        datasets = cloud_db_manager.get_dataset_list(limit=limit)
        return jsonify({'datasets': datasets, 'total': len(datasets)})
    except Exception as e:
        return handle_error(str(e))


@app.route('/cloud_dataset/<file_id>', methods=['GET'])
def get_cloud_dataset(file_id):
    """Get specific dataset metadata from cloud."""
    if not cloud_db_manager:
        return handle_error('Cloud database not available', 400)

    try:
        dataset = cloud_db_manager.get_dataset_metadata(file_id)
        return jsonify(dataset) if dataset else handle_error('Dataset not found', 404)
    except Exception as e:
        return handle_error(str(e))


@app.route('/cloud_dataset/<file_id>', methods=['DELETE'])
def delete_cloud_dataset(file_id):
    """Delete dataset from cloud database."""
    if not cloud_db_manager:
        return handle_error('Cloud database not available', 400)

    try:
        success = cloud_db_manager.delete_dataset(file_id)
        return jsonify({'success': success}) if success else handle_error('Failed to delete dataset', 400)
    except Exception as e:
        return handle_error(str(e))


@app.route('/cloud_usage', methods=['GET'])
def get_cloud_usage():
    """Get cloud storage usage statistics."""
    if not cloud_db_manager:
        return handle_error('Cloud database not available', 400)

    try:
        return jsonify(cloud_db_manager.get_storage_usage())
    except Exception as e:
        return handle_error(str(e))


# Error handlers
@app.errorhandler(413)
def too_large(e):
    """Handle file size limit exceeded."""
    return handle_error('File too large. Maximum size exceeded.', 413)


@app.errorhandler(404)
def not_found(e):
    """Handle page not found errors."""
    return handle_error('Endpoint not found', 404)


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return handle_error('Internal server error')


if __name__ == '__main__':
    print("=" * 60)
    print("Dataset Metadata Extraction Tool v2.1")
    print("=" * 60)
    print(f"🔧 Configuration: {get_config_info(CONFIG)}")
    print(f"📁 Max file size: {CONFIG['app']['max_file_size_mb']}MB")
    print(f"☁️ Cloud Database: {'✅ Enabled' if cloud_db_manager else '❌ Disabled'}")
    print(f"💾 Auto-Save: {'✅ Enabled' if is_auto_save_enabled(CONFIG) else '❌ Disabled'}")

    # Test LLM connection for direct Python runs
    llm_works = initialize_llm_status()

    print("🚀 Starting server at http://localhost:5000")
    print("=" * 60)
    app.run(debug=CONFIG['app']['debug'], host='0.0.0.0', port=5000)