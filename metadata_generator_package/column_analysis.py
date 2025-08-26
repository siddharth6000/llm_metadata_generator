"""
Column statistical analysis and type detection functionality.

Provides functions to analyze pandas DataFrame columns, compute statistics,
and detect semantic column types based on data patterns.
"""

import pandas as pd
import random


def analyze_column(column_data):
    """Main function to analyze any column type and return statistics."""
    if hasattr(column_data, 'dtype') and column_data.dtype.kind in 'iuf':
        return analyze_numeric_column(column_data)
    else:
        return analyze_categorical_column(column_data)


def analyze_numeric_column(column_data):
    """Analyze numeric column and return statistical measures."""
    try:
        unique_vals = column_data.dropna().unique()
        unique_sample = _get_sample_values(unique_vals)

        return {
            "type": str(column_data.dtype),
            "unique_values": int(column_data.nunique()),
            "sample_unique_values": [str(x) for x in unique_sample],
            "missing_values": int(column_data.isnull().sum()),
            "mean": _safe_float(column_data.mean()),
            "std": _safe_float(column_data.std()),
            "min": _safe_float(column_data.min()),
            "max": _safe_float(column_data.max())
        }
    except Exception as e:
        print(f"Error in analyze_numeric_column: {e}")
        return _create_error_stats(column_data, "numeric")


def analyze_categorical_column(column_data):
    """Analyze categorical column and return frequency statistics."""
    try:
        unique_vals = column_data.dropna().unique()
        unique_sample = _get_sample_values(unique_vals)

        # Get top value and frequency
        top_value = None
        top_freq = None
        if not column_data.mode().empty:
            top_value = column_data.mode()[0]
        if not column_data.value_counts().empty:
            top_freq = int(column_data.value_counts().iloc[0])

        return {
            "type": str(column_data.dtype),
            "unique_values": int(column_data.nunique()),
            "sample_unique_values": [str(x) for x in unique_sample],
            "missing_values": int(column_data.isnull().sum()),
            "top_value": str(top_value) if top_value is not None else None,
            "top_freq": top_freq
        }
    except Exception as e:
        print(f"Error in analyze_categorical_column: {e}")
        return _create_error_stats(column_data, "categorical")


def detect_column_type(series: pd.Series) -> str:
    """Rule-based column type detection for semantic classification."""
    unique_values = series.dropna().unique()
    n_unique = len(unique_values)
    dtype = series.dtype

    # Binary check - exactly 2 unique values
    if n_unique == 2:
        return "binary"

    # Identifier check - column name patterns
    if series.name and (series.name.lower() in ['id', 'identifier'] or series.name.lower().endswith('_id')):
        return "identifier"

    # Check if all values are alphanumeric and unique (potential identifier)
    if dtype == object and n_unique == len(series):
        non_null_series = series.dropna()
        if len(non_null_series) > 0 and non_null_series.apply(lambda x: isinstance(x, str) and x.isalnum()).all():
            return "identifier"

    # Free text check - average word count
    if dtype == object:
        non_null_series = series.dropna()
        if len(non_null_series) > 0:
            avg_word_count = non_null_series.apply(lambda x: len(str(x).split()) if isinstance(x, str) else 0).mean()
            if avg_word_count > 5:
                return "free_text"

    # Continuous check - numeric with many unique values
    if pd.api.types.is_numeric_dtype(series):
        if n_unique > 15:
            return "continuous"

    # Ordinal check - known ordinal categories
    known_ordinal = {'low', 'medium', 'high', 'bad', 'average', 'good', 'excellent', 'small', 'large'}
    if dtype == object and len(unique_values) > 0:
        if any(str(val).lower() in known_ordinal for val in unique_values if val is not None):
            return "ordinal"

    # Default categorization
    if n_unique < 15:
        return "categorical"

    return "categorical" if dtype == object else "continuous"


# Private helper functions

def _get_sample_values(unique_vals):
    """Get sample of unique values for display."""
    if len(unique_vals) <= 10:
        return unique_vals.tolist()
    else:
        return random.sample(unique_vals.tolist(), 10)


def _safe_float(value):
    """Convert value to float, return None if invalid."""
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _create_error_stats(column_data, column_type):
    """Create default statistics when analysis fails."""
    return {
        "type": str(column_data.dtype),
        "unique_values": 0,
        "sample_unique_values": [],
        "missing_values": len(column_data),
        "mean": None if column_type == "numeric" else None,
        "std": None if column_type == "numeric" else None,
        "min": None if column_type == "numeric" else None,
        "max": None if column_type == "numeric" else None,
        "top_value": None if column_type == "categorical" else None,
        "top_freq": None if column_type == "categorical" else None
    }