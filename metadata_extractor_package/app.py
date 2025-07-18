from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
import os
import tempfile
import numpy as np
from werkzeug.utils import secure_filename
from datetime import datetime

# Import functions from the updated meta_data_ex_api.py
from meta_data_ex_api import (
    analyze_column,
    detect_column_type,
    query_description_generation,
    query_type_classification,
    make_json_serializable
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Store session data in memory (in production, use Redis or database)
sessions = {}


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and initial processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400

        # Read CSV data
        try:
            dataset = pd.read_csv(file)
        except Exception as e:
            return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 400

        if dataset.empty:
            return jsonify({'error': 'CSV file is empty'}), 400

        # Generate session ID
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')

        # Store dataset in session
        sessions[session_id] = {
            'dataset': dataset,
            'filename': secure_filename(file.filename),
            'columns_processed': [],
            'metadata': {}
        }

        # Return file info and preview
        preview_data = dataset.head().fillna('').to_dict('records')

        return jsonify({
            'session_id': session_id,
            'filename': file.filename,
            'rows': len(dataset),
            'columns': len(dataset.columns),
            'column_names': list(dataset.columns),
            'preview': preview_data
        })

    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/set_dataset_info', methods=['POST'])
def set_dataset_info():
    """Store dataset name and description"""
    try:
        data = request.json
        session_id = data.get('session_id')

        if session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400

        sessions[session_id]['metadata'].update({
            'dataset_name': data.get('name'),
            'dataset_description': data.get('description')
        })

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze_column', methods=['POST'])
def analyze_column_endpoint():
    """Analyze a specific column with AI assistance - Two separate LLM calls"""
    try:
        data = request.json
        session_id = data.get('session_id')
        column_name = data.get('column_name')

        if session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400

        session_data = sessions[session_id]
        dataset = session_data['dataset']

        if column_name not in dataset.columns:
            return jsonify({'error': 'Column not found'}), 400

        # Analyze column using existing functions
        column_data = dataset[column_name]

        # Ensure we have valid data
        if column_data.empty:
            return jsonify({'error': f'Column {column_name} is empty'}), 400

        try:
            stats = analyze_column(column_data)
            detected_type = detect_column_type(column_data)
        except Exception as e:
            return jsonify({'error': f'Error analyzing column data: {str(e)}'}), 500

        # Get dataset context for LLM
        dataset_name = session_data['metadata'].get('dataset_name', 'Unknown Dataset')
        dataset_description = session_data['metadata'].get('dataset_description', 'No description')
        dataset_sample_str = dataset.head().to_string(index=False)
        previous_columns = session_data.get('columns_processed', [])

        print(f"\n🔄 Starting analysis for column: {column_name}")

        # FIRST LLM CALL: Generate description
        print("📝 LLM Call #1: Generating description...")
        try:
            description = query_description_generation(
                column_name, stats, detected_type,
                dataset_name, dataset_description, dataset_sample_str,
                previous_columns
            )
            print(f"✅ Description generated: {description[:100]}...")
        except Exception as e:
            print(f"❌ LLM description failed: {e}")
            description = f"This column represents {column_name} data in the dataset."

        # SECOND LLM CALL: Type classification using the description
        print("🎯 LLM Call #2: Classifying type based on description...")
        try:
            llm_result = query_type_classification(
                column_name, description, stats, detected_type,
                dataset_name, dataset_description, dataset_sample_str
            )
            type_confidence = llm_result.get('confidence', {})
            suggested_type = llm_result.get('suggested_type', detected_type)
            print(f"✅ Type classified as: {suggested_type}")
        except Exception as e:
            print(f"❌ LLM type classification failed: {e}")
            # Fallback to rule-based detection
            fallback_confidence = {
                "binary": 0.0, "categorical": 0.0, "ordinal": 0.0,
                "continuous": 0.0, "identifier": 0.0, "free_text": 0.0
            }
            fallback_confidence[detected_type] = 0.9
            type_confidence = fallback_confidence
            suggested_type = detected_type

        # Clean stats for JSON serialization
        clean_stats = json.loads(json.dumps(stats, default=make_json_serializable))

        return jsonify({
            'column_name': column_name,
            'stats': clean_stats,
            'detected_type': detected_type,
            'suggested_description': description,
            'suggested_type': suggested_type,
            'type_confidence': type_confidence
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reanalyze_type', methods=['POST'])
def reanalyze_type():
    """Reanalyze column type based on updated description - Third LLM call"""
    try:
        data = request.json
        session_id = data.get('session_id')
        column_name = data.get('column_name')
        updated_description = data.get('description')

        if session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400

        session_data = sessions[session_id]
        dataset = session_data['dataset']

        if column_name not in dataset.columns:
            return jsonify({'error': 'Column not found'}), 400

        # Get column stats (reuse existing analysis)
        column_data = dataset[column_name]
        stats = analyze_column(column_data)
        detected_type = detect_column_type(column_data)

        # Get dataset context
        dataset_name = session_data['metadata'].get('dataset_name', 'Unknown Dataset')
        dataset_description = session_data['metadata'].get('dataset_description', 'No description')
        dataset_sample_str = dataset.head().to_string(index=False)

        print(f"\n🔄 Reanalyzing type for column: {column_name}")
        print(f"📝 Updated description: {updated_description[:100]}...")

        # THIRD LLM CALL: Query LLM for type classification using the updated description
        print("🎯 LLM Call #3: Reclassifying type based on updated description...")
        try:
            llm_result = query_type_classification(
                column_name, updated_description, stats, detected_type,
                dataset_name, dataset_description, dataset_sample_str
            )
            suggested_type = llm_result.get('suggested_type', detected_type)
            print(f"✅ Type reclassified as: {suggested_type}")
        except Exception as e:
            print(f"❌ LLM type classification failed: {e}")
            # Fallback to rule-based detection
            suggested_type = detected_type

        return jsonify({
            'column_name': column_name,
            'suggested_type': suggested_type
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/confirm_column', methods=['POST'])
def confirm_column():
    """Save user-confirmed column metadata"""
    try:
        data = request.json
        session_id = data.get('session_id')
        column_name = data.get('column_name')
        column_type = data.get('type')
        description = data.get('description')

        if session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400

        session_data = sessions[session_id]
        dataset = session_data['dataset']

        # Get column stats
        column_data = dataset[column_name]
        stats = analyze_column(column_data)

        # Create column metadata entry
        column_entry = {
            "name": column_name,
            "description": description,
            "type": column_type,
            "missing_values": int(stats.get("missing_values", 0)),
            "unique_values": int(stats.get("unique_values", 0))
        }

        # Add numerical stats for continuous columns
        if column_type == "continuous" and stats.get("mean") is not None:
            column_entry.update({
                "mean": float(stats.get("mean")),
                "std": float(stats.get("std")) if stats.get("std") is not None else None,
                "min": float(stats.get("min")) if stats.get("min") is not None else None,
                "max": float(stats.get("max")) if stats.get("max") is not None else None
            })

        # Add to processed columns
        session_data['columns_processed'].append(column_entry)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_metadata', methods=['POST'])
def get_metadata():
    """Retrieve complete metadata for the dataset"""
    try:
        data = request.json
        session_id = data.get('session_id')

        if session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400

        session_data = sessions[session_id]

        metadata = {
            "dataset_name": session_data['metadata'].get('dataset_name'),
            "dataset_description": session_data['metadata'].get('dataset_description'),
            "columns": session_data['columns_processed']
        }

        return jsonify(metadata)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download_metadata', methods=['POST'])
def download_metadata():
    """Generate and download metadata JSON file"""
    try:
        data = request.json
        session_id = data.get('session_id')

        if session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400

        session_data = sessions[session_id]

        metadata = {
            "dataset_name": session_data['metadata'].get('dataset_name'),
            "dataset_description": session_data['metadata'].get('dataset_description'),
            "columns": session_data['columns_processed']
        }

        # Clean metadata for JSON serialization
        clean_metadata = json.loads(json.dumps(metadata, default=make_json_serializable))

        # Create temporary file
        dataset_name = metadata.get('dataset_name', 'dataset')
        filename = f"{dataset_name.replace(' ', '_').lower()}_metadata.json"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")

        with open(filepath, 'w') as f:
            json.dump(clean_metadata, f, indent=4)

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(sessions),
        'version': '1.0.0'
    })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error'}), 500


# Cleanup function to remove old sessions (optional)
def cleanup_old_sessions():
    """Remove sessions older than 1 hour to prevent memory leaks"""
    import time
    current_time = time.time()
    cutoff_time = current_time - 3600  # 1 hour ago

    sessions_to_remove = []
    for session_id in sessions:
        try:
            # Extract timestamp from session_id
            timestamp_str = session_id.split('_')[0] + session_id.split('_')[1]
            session_time = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S').timestamp()
            if session_time < cutoff_time:
                sessions_to_remove.append(session_id)
        except:
            # If we can't parse the timestamp, remove the session
            sessions_to_remove.append(session_id)

    for session_id in sessions_to_remove:
        del sessions[session_id]
        print(f"Cleaned up old session: {session_id}")


if __name__ == '__main__':
    print("=" * 60)
    print("Dataset Metadata Extraction Tool - Web Interface")
    print("=" * 60)
    print("Features:")
    print("   • AI-powered column description generation (LLM Call #1)")
    print("   • AI-powered column type detection (LLM Call #2)")
    print("   • Interactive description updates (LLM Call #3)")
    print("   • Column navigation (back/forth between columns)")
    print("   • Professional metadata export")
    print()
    print("🔧 Configuration:")
    print(f"   • Max file size: {app.config['MAX_CONTENT_LENGTH'] // 1024 // 1024}MB")
    print("   • LLM API: Configured in meta_data_ex_api.py")
    print()
    print("Starting server...")
    print("   • Web interface: http://localhost:5000")
    print("   • Health check: http://localhost:5000/health")
    print()
    print("⚠️  Make sure your LLM server is running for AI features!")
    print("=" * 60)

    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)