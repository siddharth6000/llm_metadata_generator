"""
Optimized session data management
"""

import time
from datetime import datetime
from column_analysis import analyze_column

# Global session storage
sessions = {}

def create_session(dataset, extra_content="", extra_filename=""):
    """Create a new session with uploaded data"""
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')

    sessions[session_id] = {
        'dataset': dataset,
        'columns_processed': [],
        'metadata': {},
        'extra_content': extra_content,
        'extra_filename': extra_filename,
        'analysis_results': {},
        'created_at': time.time()
    }

    print(f"Created session {session_id} with dataset shape: {dataset.shape}")
    return session_id

def get_session(session_id):
    """Retrieve session data"""
    return sessions.get(session_id)

def update_dataset_metadata(session_id, name, description):
    """Update dataset name and description"""
    if session_id in sessions:
        sessions[session_id]['metadata'].update({
            'dataset_name': name,
            'dataset_description': description
        })
        return True
    return False

def store_column_analysis(session_id, column_name, analysis_result):
    """Store column analysis results in session"""
    if session_id not in sessions:
        return False

    if 'analysis_results' not in sessions[session_id]:
        sessions[session_id]['analysis_results'] = {}

    sessions[session_id]['analysis_results'][column_name] = {
        'stats': analysis_result.get('stats', {}),
        'detected_type': analysis_result.get('detected_type', ''),
        'description': analysis_result.get('suggested_description', ''),
        'type': analysis_result.get('suggested_type', ''),
        'confidence': analysis_result.get('type_confidence', {})
    }
    return True

def update_column_analysis(session_id, column_name, updates):
    """Update specific fields in column analysis"""
    if (session_id in sessions and
        'analysis_results' in sessions[session_id] and
        column_name in sessions[session_id]['analysis_results']):

        sessions[session_id]['analysis_results'][column_name].update(updates)
        return True
    return False

def confirm_column(session_id, column_name, column_type, description):
    """Confirm and save final column metadata"""
    session_data = get_session(session_id)
    if not session_data or column_name not in session_data['dataset'].columns:
        return False

    column_data = session_data['dataset'][column_name]
    stats = analyze_column(column_data)

    # Create column metadata entry
    column_entry = {
        "name": column_name,
        "description": description or f"Column {column_name}",
        "type": column_type or "categorical",
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

    # Update or add column
    existing_columns = sessions[session_id]['columns_processed']
    for i, existing_col in enumerate(existing_columns):
        if existing_col['name'] == column_name:
            existing_columns[i] = column_entry
            return True

    existing_columns.append(column_entry)
    return True

def get_analysis_context(session_id):
    """Get analysis context for AI processing"""
    session_data = get_session(session_id)
    if not session_data:
        return {}

    dataset = session_data['dataset']
    metadata = session_data['metadata']

    # Get previous columns
    previous_columns = []
    analysis_results = session_data.get('analysis_results', {})
    for col_name, col_data in analysis_results.items():
        if col_data.get('description') and col_data.get('type'):
            previous_columns.append({
                'name': col_name,
                'type': col_data.get('type'),
                'description': col_data.get('description')
            })

    return {
        'dataset_name': metadata.get('dataset_name', 'Unknown Dataset'),
        'dataset_description': metadata.get('dataset_description', 'No description'),
        'dataset_sample_str': dataset.head().to_string(index=False),
        'previous_columns': previous_columns,
        'additional_context': session_data.get('extra_content', '')
    }

def auto_confirm_all_columns(session_id):
    """Auto-confirm all analyzed columns"""
    session_data = get_session(session_id)
    if not session_data:
        return False

    dataset = session_data['dataset']
    analysis_results = session_data.get('analysis_results', {})

    for column_name in dataset.columns:
        if column_name in analysis_results:
            analysis_data = analysis_results[column_name]
            column_type = analysis_data.get('type', 'categorical')
            description = analysis_data.get('description', f'Column {column_name}')
        else:
            # Fallback for unanalyzed columns
            column_type = 'categorical'
            description = f'Column {column_name}'

        confirm_column(session_id, column_name, column_type, description)

    return True

def cleanup_old_sessions(max_age_hours=1):
    """Remove sessions older than specified hours"""
    current_time = time.time()
    cutoff_time = current_time - (max_age_hours * 3600)

    sessions_to_remove = [
        session_id for session_id, session_data in sessions.items()
        if session_data.get('created_at', 0) < cutoff_time
    ]

    for session_id in sessions_to_remove:
        del sessions[session_id]

    return len(sessions_to_remove)

def get_session_count():
    """Get total number of active sessions"""
    return len(sessions)

def debug_session_data(session_id):
    """Debug function to print session data"""
    session_data = get_session(session_id)
    if not session_data:
        print(f"Session {session_id} not found")
        return

    print(f"=== DEBUG SESSION {session_id} ===")
    print(f"Dataset shape: {session_data['dataset'].shape}")
    print(f"Metadata: {session_data['metadata']}")
    print(f"Columns processed: {len(session_data['columns_processed'])}")
    print(f"Analysis results: {len(session_data['analysis_results'])}")
    print("=== END DEBUG ===")