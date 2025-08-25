"""
Optimized metadata export functionality with clean filenames
"""

import json
import numpy as np
import pandas as pd
import re
import zipfile
import os
import tempfile
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS

# Define namespaces
DQV = Namespace("http://www.w3.org/ns/dqv#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SCHEMA = Namespace("http://schema.org/")
DATASET = Namespace("http://example.org/dataset/")
METRICS = Namespace("http://example.org/metrics/")

def make_json_serializable(obj):
    """Convert numpy types to JSON-serializable types"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj

def create_safe_filename(name):
    """Create a safe filename from dataset name"""
    if not name:
        return 'dataset'
    safe_name = str(name).replace(' ', '_').replace('-', '_').lower()
    safe_name = re.sub(r'[^\w\-_]', '', safe_name)
    return safe_name if safe_name else 'dataset'

def get_file_paths(metadata, session_id, file_extension, use_clean_name=False):
    """Generate file paths for exports"""
    dataset_name = metadata.get('dataset_name', 'dataset')
    safe_name = create_safe_filename(dataset_name)

    if use_clean_name:
        # Use clean filename without session ID - for final user-facing files
        filename = f"{safe_name}_metadata.{file_extension}"
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
    else:
        # Use session ID for temporary internal files to avoid conflicts
        filename = f"{safe_name}_metadata.{file_extension}"
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, f"{session_id}_{filename}")

    return filepath, filename

def export_json(metadata, session_id):
    """Export metadata in JSON format"""
    try:
        clean_metadata = json.loads(json.dumps(metadata, default=make_json_serializable))
        filepath, filename = get_file_paths(metadata, session_id, 'json')

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_metadata, f, indent=4, ensure_ascii=False)

        return filepath, filename
    except Exception as e:
        print(f"Error in export_json: {e}")
        raise

def export_dqv(metadata, session_id):
    """Export metadata in DQV (Turtle) format"""
    try:
        dqv_content = create_dqv_metadata(metadata)
        filepath, filename = get_file_paths(metadata, session_id, 'ttl')

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dqv_content)

        return filepath, filename
    except Exception as e:
        print(f"Error in export_dqv: {e}")
        raise

def export_zip(metadata, session_id, dataset, extra_filename="", extra_content=""):
    """Export complete package as ZIP file with clean filename"""
    try:
        safe_name = create_safe_filename(metadata.get('dataset_name', 'dataset'))

        # Create clean ZIP filename without session ID or UUID
        clean_zip_filename = f"{safe_name}_package.zip"

        # But create the actual file with session ID to avoid conflicts during processing
        temp_dir = tempfile.gettempdir()
        zip_filepath = os.path.join(temp_dir, f"{session_id}_{clean_zip_filename}")

        print(f"📦 Creating ZIP file: {clean_zip_filename}")
        print(f"📁 Temp path: {zip_filepath}")

        os.makedirs(os.path.dirname(zip_filepath), exist_ok=True)

        # Create temporary files for ZIP contents
        json_filepath, json_filename = export_json(metadata, session_id)
        dqv_filepath, dqv_filename = export_dqv(metadata, session_id)

        # Create CSV file with clean name
        csv_filename = f"{safe_name}_dataset.csv"
        csv_filepath = os.path.join(temp_dir, f"{session_id}_{csv_filename}")
        dataset.to_csv(csv_filepath, index=False)

        # Create extra file if content exists
        extra_filepath = None
        if extra_content and extra_filename:
            # Keep original extra filename for clarity
            extra_filepath = os.path.join(temp_dir, f"{session_id}_{extra_filename}")
            with open(extra_filepath, 'w', encoding='utf-8') as f:
                f.write(extra_content)

        # Create ZIP with clean internal filenames
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add files to ZIP with clean names (no session IDs in ZIP contents)
            zipf.write(csv_filepath, csv_filename)
            zipf.write(json_filepath, json_filename)
            zipf.write(dqv_filepath, dqv_filename)

            if extra_filepath and os.path.exists(extra_filepath):
                zipf.write(extra_filepath, extra_filename)

            # Add README
            readme_content = create_readme_content(metadata, extra_filename)
            zipf.writestr("README.txt", readme_content)

        # Cleanup temporary files
        for filepath in [json_filepath, dqv_filepath, csv_filepath, extra_filepath]:
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass

        print(f"✅ ZIP created successfully: {clean_zip_filename}")
        print(f"📏 ZIP file size: {os.path.getsize(zip_filepath)} bytes")

        # Return the temp path for processing, but clean filename for display
        return zip_filepath, clean_zip_filename

    except Exception as e:
        print(f"Error in export_zip: {e}")
        raise

def create_readme_content(metadata, extra_filename=""):
    """Create README content for ZIP package"""
    dataset_name = metadata.get('dataset_name', 'Dataset')
    dataset_description = metadata.get('dataset_description', 'No description')
    columns = metadata.get('columns', [])

    readme = f"""# {dataset_name} - Complete Data Package

## Description
{dataset_description}

## Package Contents
- **Dataset**: {create_safe_filename(dataset_name)}_dataset.csv (Original data)
- **JSON Metadata**: {create_safe_filename(dataset_name)}_metadata.json (Structured metadata)
- **DQV Metadata**: {create_safe_filename(dataset_name)}_metadata.ttl (W3C DQV format)
"""

    if extra_filename:
        readme += f"- **Additional Context**: {extra_filename} (Additional documentation)\n"

    readme += f"\n## Column Information ({len(columns)} columns)\n"

    for i, column in enumerate(columns, 1):
        readme += f"""
### {i}. {column.get('name', 'Unknown')}
- **Type**: {column.get('type', 'Unknown')}
- **Description**: {column.get('description', 'No description')}
- **Missing Values**: {column.get('missing_values', 'N/A')}
- **Unique Values**: {column.get('unique_values', 'N/A')}
"""
        # Add stats for continuous columns
        if column.get('type') == 'continuous' and 'mean' in column:
            readme += f"- **Mean**: {column.get('mean', 'N/A')}\n"
            readme += f"- **Std Dev**: {column.get('std', 'N/A')}\n"
            readme += f"- **Range**: {column.get('min', 'N/A')} - {column.get('max', 'N/A')}\n"

    readme += f"""

## Metadata Generated
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Tool**: Dataset Metadata Extraction Tool v2.1
- **AI-Powered**: Column descriptions and types generated with AI assistance

## Usage
- CSV file: Open in any spreadsheet application or data analysis tool
- JSON metadata: For programmatic access and integration
- DQV metadata: For semantic web and linked data applications
"""

    return readme

def create_dqv_metadata(json_metadata):
    """Convert JSON metadata to DQV RDF format"""
    try:
        g = Graph()

        # Bind namespaces
        namespaces = {
            "dqv": DQV, "dcat": DCAT, "prov": PROV, "dcterms": DCTERMS,
            "skos": SKOS, "schema": SCHEMA, "dataset": DATASET, "metrics": METRICS
        }
        for prefix, namespace in namespaces.items():
            g.bind(prefix, namespace)

        # Create dataset
        dataset_name = json_metadata.get("dataset_name", "dataset")
        dataset_name_clean = create_safe_filename(dataset_name)
        dataset_uri = DATASET[dataset_name_clean]

        g.add((dataset_uri, RDF.type, DCAT.Dataset))
        g.add((dataset_uri, DCTERMS.title, Literal(dataset_name)))
        g.add((dataset_uri, DCTERMS.description, Literal(json_metadata.get("dataset_description", "No description"))))
        g.add((dataset_uri, DCTERMS.created, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

        columns = json_metadata.get("columns", [])

        # Add column count metric
        add_metric(g, METRICS.columnCount, "Column Count", "Total columns in dataset",
                  dataset_uri, len(columns), XSD.integer, DQV.completeness)

        # Process each column
        for column in columns:
            if not column or not column.get('name'):
                continue

            column_name_clean = create_safe_filename(column["name"])
            column_uri = DATASET[f"{dataset_name_clean}/column/{column_name_clean}"]

            # Column description
            g.add((column_uri, RDF.type, SCHEMA.PropertyValue))
            g.add((column_uri, SCHEMA.name, Literal(column["name"])))
            g.add((column_uri, SCHEMA.description, Literal(column.get("description", "No description"))))
            g.add((column_uri, SCHEMA.valueReference, Literal(column.get("type", "unknown"))))
            g.add((dataset_uri, SCHEMA.variableMeasured, column_uri))

            # Add quality metrics
            add_column_metrics(g, column_uri, column)

        # Add provenance
        add_provenance(g, dataset_uri)

        return g.serialize(format='turtle')

    except Exception as e:
        print(f"Error in create_dqv_metadata: {e}")
        # Return minimal DQV on error
        return f"""@prefix dqv: <http://www.w3.org/ns/dqv#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix dataset: <http://example.org/dataset/> .

dataset:dataset a dcat:Dataset ;
    dcterms:title "{json_metadata.get('dataset_name', 'Dataset')}" ;
    dcterms:description "{json_metadata.get('dataset_description', 'No description')}" ;
    dcterms:created "{datetime.now().isoformat()}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
"""

def add_metric(g, metric_uri, label, description, subject_uri, value, datatype, dimension):
    """Add a quality metric to the graph"""
    g.add((metric_uri, RDF.type, DQV.Metric))
    g.add((metric_uri, SKOS.prefLabel, Literal(label)))
    g.add((metric_uri, DCTERMS.description, Literal(description)))
    g.add((metric_uri, DQV.inDimension, dimension))

    measurement = BNode()
    g.add((measurement, RDF.type, DQV.QualityMeasurement))
    g.add((measurement, DQV.computedOn, subject_uri))
    g.add((measurement, DQV.isMeasurementOf, metric_uri))
    g.add((measurement, DQV.value, Literal(value, datatype=datatype)))

def add_column_metrics(g, column_uri, column):
    """Add quality metrics for a column"""
    try:
        # Data type metric
        add_metric(g, METRICS.dataType, "Data Type", "Semantic data type",
                  column_uri, column.get("type", "unknown"), None, DQV.consistency)

        # Missing values metric
        add_metric(g, METRICS.missingValues, "Missing Values", "Number of missing values",
                  column_uri, column.get("missing_values", 0), XSD.integer, DQV.completeness)

        # Unique values metric
        add_metric(g, METRICS.uniqueValues, "Unique Values", "Number of unique values",
                  column_uri, column.get("unique_values", 0), XSD.integer, DQV.completeness)

        # Numerical statistics for continuous columns
        if column.get("type") == "continuous" and "mean" in column and column["mean"] is not None:
            for stat, label, desc in [
                ("mean", "Mean Value", "Average value"),
                ("std", "Standard Deviation", "Standard deviation"),
                ("min", "Minimum Value", "Minimum value"),
                ("max", "Maximum Value", "Maximum value")
            ]:
                if stat in column and column[stat] is not None:
                    add_metric(g, getattr(METRICS, stat + 'Value'), label, desc,
                              column_uri, column[stat], XSD.double, DQV.accuracy)

    except Exception as e:
        print(f"Error adding column metrics: {e}")

def add_provenance(g, dataset_uri):
    """Add provenance information"""
    try:
        activity = BNode()
        g.add((activity, RDF.type, PROV.Activity))
        g.add((activity, RDFS.label, Literal("Dataset Metadata Extraction")))
        g.add((activity, PROV.startedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        g.add((activity, PROV.used, dataset_uri))

        tool = DATASET.MetadataExtractionTool
        g.add((tool, RDF.type, PROV.SoftwareAgent))
        g.add((tool, RDFS.label, Literal("Dataset Metadata Extraction Tool")))
        g.add((activity, PROV.wasAssociatedWith, tool))
    except Exception as e:
        print(f"Error adding provenance: {e}")