"""Column statistical analysis and type detection functionality."""

import pandas as pd
import random


def analyze_column(column_data):
    """Main function to analyze any column type"""
    if hasattr(column_data, 'dtype') and column_data.dtype.kind in 'iuf':
        return analyze_numeric_column(column_data)
    else:
        return analyze_categorical_column(column_data)


def analyze_numeric_column(column_data):
    """Analyze numeric column and return statistics"""
    try:
        unique_vals = column_data.dropna().unique()
        unique_sample = unique_vals.tolist() if len(unique_vals) <= 10 else random.sample(unique_vals.tolist(), 10)

        return {
            "type": str(column_data.dtype),
            "unique_values": int(column_data.nunique()),
            "sample_unique_values": [str(x) for x in unique_sample],
            "missing_values": int(column_data.isnull().sum()),
            "mean": float(column_data.mean()) if not pd.isna(column_data.mean()) else None,
            "std": float(column_data.std()) if not pd.isna(column_data.std()) else None,
            "min": float(column_data.min()) if not pd.isna(column_data.min()) else None,
            "max": float(column_data.max()) if not pd.isna(column_data.max()) else None
        }
    except Exception as e:
        print(f"Error in analyze_numeric_column: {e}")
        return {
            "type": str(column_data.dtype),
            "unique_values": 0,
            "sample_unique_values": [],
            "missing_values": len(column_data),
            "mean": None,
            "std": None,
            "min": None,
            "max": None
        }


def analyze_categorical_column(column_data):
    """Analyze categorical column and return statistics"""
    try:
        unique_vals = column_data.dropna().unique()
        unique_sample = unique_vals.tolist() if len(unique_vals) <= 10 else random.sample(unique_vals.tolist(), 10)

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
        return {
            "type": str(column_data.dtype),
            "unique_values": 0,
            "sample_unique_values": [],
            "missing_values": len(column_data),
            "top_value": None,
            "top_freq": None
        }


def detect_column_type(series: pd.Series) -> str:
    """Rule-based column type detection"""
    unique_values = series.dropna().unique()
    n_unique = len(unique_values)
    dtype = series.dtype

    # Binary check
    if n_unique == 2:
        return "binary"

    # Identifier check
    if series.name and (series.name.lower() in ['id', 'identifier'] or series.name.lower().endswith('_id')):
        return "identifier"

    # Check if all values are alphanumeric and unique (potential identifier)
    if dtype == object and n_unique == len(series):
        non_null_series = series.dropna()
        if len(non_null_series) > 0 and non_null_series.apply(lambda x: isinstance(x, str) and x.isalnum()).all():
            return "identifier"

    # Free text check
    if dtype == object:
        non_null_series = series.dropna()
        if len(non_null_series) > 0:
            avg_word_count = non_null_series.apply(lambda x: len(str(x).split()) if isinstance(x, str) else 0).mean()
            if avg_word_count > 5:
                return "free_text"

    # Continuous check
    if pd.api.types.is_numeric_dtype(series):
        if n_unique > 15:
            return "continuous"

    # Ordinal check (manual or based on known categories)
    known_ordinal = {'low', 'medium', 'high', 'bad', 'average', 'good', 'excellent', 'small', 'large'}
    if dtype == object and len(unique_values) > 0:
        if any(str(val).lower() in known_ordinal for val in unique_values if val is not None):
            return "ordinal"

    # Categorical (fallback)
    if n_unique < 15:
        return "categorical"

    return "categorical" if dtype == object else "continuous"