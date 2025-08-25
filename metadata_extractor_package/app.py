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

# Initialize Flask app
app = Flask(__name__)

# Load configuration (no more .env files!)
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


def handle_error(error_msg, status_code=500):
    """Unified error handling"""
    print(f"Error: {error_msg}")
    return jsonify({'error': error_msg}), status_code


def save_to_cloud(session_id, metadata, zip_path, original_filename):
    """Enhanced cloud save function with better error handling and logging"""
    if not cloud_db_manager:
        print("❌ Cloud database manager is not available")
        return False

    if not session_id:
        print("❌ Session ID is missing")
        return False

    if not metadata or not metadata.get('columns'):
        print("❌ Metadata is missing or has no columns")
        return False

    if not os.path.exists(zip_path):
        print(f"❌ ZIP file not found: {zip_path}")
        return False

    try:
        file_size = os.path.getsize(zip_path)
        print(f"💾 Saving to cloud database...")
        print(f"   Session ID: {session_id}")
        print(f"   Dataset: {metadata.get('dataset_name', 'Unknown')}")
        print(f"   Columns: {len(metadata.get('columns', []))}")
        print(f"   ZIP file: {zip_path}")
        print(f"   File size: {file_size} bytes")

        result = cloud_db_manager.save_dataset_metadata(
            session_id=session_id,
            metadata=metadata,
            zip_file_path=zip_path,
            original_filename=original_filename
        )

        print(f"📊 Cloud save result: {result}")

        if result and result.get('success'):
            print(f"✅ Cloud save successful!")
            print(f"   File ID: {result.get('file_id')}")
            print(f"   ZIP filename: {result.get('zip_filename')}")
            return True
        else:
            error_msg = result.get('error') if result else 'No result returned'
            print(f"❌ Cloud save failed: {error_msg}")
            return False

    except Exception as e:
        print(f"❌ Cloud save error: {e}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
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
    try:
        data = request.json
        success = update_dataset_metadata(data.get('session_id'), data.get('name'), data.get('description'))
        return jsonify({'success': success}) if success else handle_error('Invalid session', 400)
    except Exception as e:
        return handle_error(str(e))


@app.route('/analyze_column', methods=['POST'])
def analyze_column_endpoint():
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
        print(f"   Dataset: {metadata.get('dataset_name')}")
        print(f"   Columns: {len(metadata.get('columns', []))}")

        # Auto-save to cloud database if enabled
        if cloud_db_manager and is_auto_save_enabled(CONFIG) and len(metadata.get('columns', [])) > 0:
            try:
                print("🔄 Auto-save is enabled, attempting to save...")

                # Get session data for ZIP creation
                dataset = session_data['dataset']
                extra_content = session_data.get('extra_content', '')
                extra_filename = session_data.get('extra_filename', '')

                print(f"📁 Dataset shape: {dataset.shape}")
                print(f"📄 Extra file: {extra_filename}")

                # Generate ZIP file
                print("🗜️  Creating ZIP file...")
                zip_filepath, zip_filename = export_zip(
                    metadata, session_id, dataset, extra_filename, extra_content
                )

                print(f"📦 ZIP created: {zip_filename}")
                print(f"📁 ZIP path: {zip_filepath}")

                # Verify ZIP file was created
                if not os.path.exists(zip_filepath):
                    print("❌ ZIP file was not created")
                    raise Exception("ZIP file creation failed")

                file_size = os.path.getsize(zip_filepath)
                if file_size == 0:
                    print("❌ ZIP file is empty")
                    raise Exception("ZIP file is empty")

                print(f"✅ ZIP file verified: {file_size} bytes")

                # Save to cloud
                original_filename = f"{metadata.get('dataset_name', 'dataset')}.csv"
                save_success = save_to_cloud(session_id, metadata, zip_filepath, original_filename)

                # Clean up temporary ZIP file
                try:
                    if os.path.exists(zip_filepath):
                        os.remove(zip_filepath)
                        print("🧹 Cleaned up temporary ZIP file")
                except Exception as cleanup_error:
                    print(f"⚠️ Could not clean up ZIP file: {cleanup_error}")

                if save_success:
                    print("🎉 Auto-save completed successfully!")
                else:
                    print("⚠️ Auto-save failed but continuing...")

            except Exception as auto_save_error:
                print(f"⚠️ Auto-save to cloud database failed: {auto_save_error}")
                print(f"🔍 Auto-save traceback: {traceback.format_exc()}")
                # Don't fail the main request if cloud save fails
        else:
            if not cloud_db_manager:
                print("ℹ️  Cloud database manager not available")
            elif not is_auto_save_enabled(CONFIG):
                print("ℹ️  Auto-save is disabled in configuration")
            elif len(metadata.get('columns', [])) == 0:
                print("ℹ️  No columns to save")

        return jsonify(metadata)

    except Exception as e:
        return handle_error(str(e))


@app.route('/download_metadata', methods=['POST'])
def download_metadata():
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
                    save_success = save_to_cloud(session_id, metadata, filepath, original_filename)
                    if save_success:
                        print("✅ ZIP download saved to cloud successfully")
                    else:
                        print("⚠️ ZIP download cloud save failed")
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


# Cloud database routes (if enabled)
@app.route('/cloud_datasets', methods=['GET'])
def get_cloud_datasets():
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
    if not cloud_db_manager:
        return handle_error('Cloud database not available', 400)

    try:
        dataset = cloud_db_manager.get_dataset_metadata(file_id)
        return jsonify(dataset) if dataset else handle_error('Dataset not found', 404)
    except Exception as e:
        return handle_error(str(e))


@app.route('/cloud_dataset/<file_id>', methods=['DELETE'])
def delete_cloud_dataset(file_id):
    if not cloud_db_manager:
        return handle_error('Cloud database not available', 400)

    try:
        success = cloud_db_manager.delete_dataset(file_id)
        return jsonify({'success': success}) if success else handle_error('Failed to delete dataset', 400)
    except Exception as e:
        return handle_error(str(e))


@app.route('/cloud_usage', methods=['GET'])
def get_cloud_usage():
    if not cloud_db_manager:
        return handle_error('Cloud database not available', 400)

    try:
        return jsonify(cloud_db_manager.get_storage_usage())
    except Exception as e:
        return handle_error(str(e))


@app.route('/auto_confirm_columns', methods=['POST'])
def auto_confirm_columns():
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


@app.route('/test_cloud_save', methods=['POST'])
def test_cloud_save():
    """Test endpoint to manually trigger cloud save"""
    try:
        session_id = request.json.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id required'}), 400

        print(f"🧪 Testing cloud save for session: {session_id}")

        session_data = get_session(session_id)
        if not session_data:
            return jsonify({'error': 'Invalid session'}), 400

        # Create metadata
        metadata = {
            "dataset_name": session_data['metadata'].get('dataset_name', 'Test Dataset'),
            "dataset_description": session_data['metadata'].get('dataset_description', 'Test Description'),
            "columns": session_data.get('columns_processed', [])
        }

        if len(metadata['columns']) == 0:
            return jsonify({'error': 'No columns to save'}), 400

        # Create ZIP
        dataset = session_data['dataset']
        zip_filepath, zip_filename = export_zip(
            metadata, session_id, dataset,
            session_data.get('extra_filename', ''),
            session_data.get('extra_content', '')
        )

        # Save to cloud
        success = save_to_cloud(
            session_id, metadata, zip_filepath,
            f"{metadata.get('dataset_name', 'dataset')}.csv"
        )

        # Cleanup
        if os.path.exists(zip_filepath):
            os.remove(zip_filepath)

        return jsonify({
            'success': success,
            'message': 'Cloud save test completed',
            'columns_count': len(metadata['columns']),
            'cloud_db_available': cloud_db_manager is not None,
            'auto_save_enabled': is_auto_save_enabled(CONFIG)
        })

    except Exception as e:
        print(f"❌ Test cloud save failed: {e}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
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
            'version': '2.1.0'
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route("/supabase-health")
def supabase_health():
    if not cloud_db_manager:
        return jsonify({'error': 'Cloud database not available'}), 400
    return cloud_db_manager.health_check()


# Error handlers
@app.errorhandler(413)
def too_large(e):
    return handle_error('File too large. Maximum size exceeded.', 413)


@app.errorhandler(404)
def not_found(e):
    return handle_error('Endpoint not found', 404)


@app.errorhandler(500)
def internal_error(e):
    return handle_error('Internal server error')


if __name__ == '__main__':
    print("=" * 60)
    print("Dataset Metadata Extraction Tool v2.1")
    print("=" * 60)
    print(f"🔧 Configuration: {get_config_info(CONFIG)}")
    print(f"📁 Max file size: {CONFIG['app']['max_file_size_mb']}MB")
    print(f"☁️ Cloud Database: {'✅ Enabled' if cloud_db_manager else '❌ Disabled'}")
    print(f"🔄 Auto-Save: {'✅ Enabled' if is_auto_save_enabled(CONFIG) else '❌ Disabled'}")

    # Quick LLM test
    print("🧪 Testing LLM connection...")
    llm_works = test_llm_connection(CONFIG, openai_client)

    if llm_works:
        print("🤖 LLM Status: ✅ Connected")
        print("🚀 Starting server at http://localhost:5000")
        print("=" * 60)
        app.run(debug=CONFIG['app']['debug'], host='0.0.0.0', port=5000)
    else:
        print("🤖 LLM Status: ❌ Failed")
        print("\n💀 Cannot start - LLM connection failed!")
        print("Please check your API key/endpoint in config.yaml")
        sys.exit(1)

    app.run(debug=CONFIG['app']['debug'], host='0.0.0.0', port=5000)