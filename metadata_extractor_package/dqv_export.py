"""
DQV (Data Quality Vocabulary) Export Module
Converts dataset metadata to DQV RDF format following W3C standards
"""

from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS, FOAF
from datetime import datetime
import json

# Define DQV and related namespaces
DQV = Namespace("http://www.w3.org/ns/dqv#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SCHEMA = Namespace("http://schema.org/")

# Custom namespace for our dataset
DATASET = Namespace("http://example.org/dataset/")
METRICS = Namespace("http://example.org/metrics/")


def create_dqv_metadata(json_metadata):
    """
    Convert JSON metadata to DQV RDF format

    Args:
        json_metadata (dict): The metadata in JSON format

    Returns:
        str: DQV metadata in Turtle format
    """

    # Create RDF graph
    g = Graph()

    # Bind namespaces
    g.bind("dqv", DQV)
    g.bind("dcat", DCAT)
    g.bind("prov", PROV)
    g.bind("dcterms", DCTERMS)
    g.bind("foaf", FOAF)
    g.bind("skos", SKOS)
    g.bind("schema", SCHEMA)
    g.bind("dataset", DATASET)
    g.bind("metrics", METRICS)

    # Dataset URI
    dataset_name_clean = json_metadata["dataset_name"].replace(" ", "_").replace("-", "_")
    dataset_uri = DATASET[dataset_name_clean]

    # Create dataset description
    g.add((dataset_uri, RDF.type, DCAT.Dataset))
    g.add((dataset_uri, DCTERMS.title, Literal(json_metadata["dataset_name"])))
    g.add((dataset_uri, DCTERMS.description, Literal(json_metadata["dataset_description"])))
    g.add((dataset_uri, DCTERMS.created, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

    # Add column count as a quality metric
    column_count_metric = METRICS.columnCount
    g.add((column_count_metric, RDF.type, DQV.Metric))
    g.add((column_count_metric, SKOS.prefLabel, Literal("Column Count")))
    g.add((column_count_metric, DCTERMS.description, Literal("Total number of columns in the dataset")))
    g.add((column_count_metric, DQV.inDimension, DQV.completeness))

    # Column count measurement
    column_count_measurement = BNode()
    g.add((column_count_measurement, RDF.type, DQV.QualityMeasurement))
    g.add((column_count_measurement, DQV.computedOn, dataset_uri))
    g.add((column_count_measurement, DQV.isMeasurementOf, column_count_metric))
    g.add((column_count_measurement, DQV.value, Literal(len(json_metadata["columns"]), datatype=XSD.integer)))

    # Process each column
    for col_idx, column in enumerate(json_metadata["columns"]):
        column_name_clean = column["name"].replace(" ", "_").replace("-", "_")
        column_uri = DATASET[f"{dataset_name_clean}/column/{column_name_clean}"]

        # Column as a distribution/field
        g.add((column_uri, RDF.type, SCHEMA.PropertyValue))
        g.add((column_uri, SCHEMA.name, Literal(column["name"])))
        g.add((column_uri, SCHEMA.description, Literal(column["description"])))
        g.add((column_uri, SCHEMA.valueReference, Literal(column["type"])))
        g.add((dataset_uri, SCHEMA.variableMeasured, column_uri))

        # Data type quality metric
        data_type_metric = METRICS.dataType
        g.add((data_type_metric, RDF.type, DQV.Metric))
        g.add((data_type_metric, SKOS.prefLabel, Literal("Data Type")))
        g.add((data_type_metric, DCTERMS.description, Literal("Semantic data type of the column")))
        g.add((data_type_metric, DQV.inDimension, DQV.consistency))

        # Data type measurement
        data_type_measurement = BNode()
        g.add((data_type_measurement, RDF.type, DQV.QualityMeasurement))
        g.add((data_type_measurement, DQV.computedOn, column_uri))
        g.add((data_type_measurement, DQV.isMeasurementOf, data_type_metric))
        g.add((data_type_measurement, DQV.value, Literal(column["type"])))

        # Missing values metric
        missing_values_metric = METRICS.missingValues
        g.add((missing_values_metric, RDF.type, DQV.Metric))
        g.add((missing_values_metric, SKOS.prefLabel, Literal("Missing Values")))
        g.add((missing_values_metric, DCTERMS.description, Literal("Number of missing/null values in the column")))
        g.add((missing_values_metric, DQV.inDimension, DQV.completeness))

        # Missing values measurement
        missing_values_measurement = BNode()
        g.add((missing_values_measurement, RDF.type, DQV.QualityMeasurement))
        g.add((missing_values_measurement, DQV.computedOn, column_uri))
        g.add((missing_values_measurement, DQV.isMeasurementOf, missing_values_metric))
        g.add((missing_values_measurement, DQV.value, Literal(column["missing_values"], datatype=XSD.integer)))

        # Unique values metric
        unique_values_metric = METRICS.uniqueValues
        g.add((unique_values_metric, RDF.type, DQV.Metric))
        g.add((unique_values_metric, SKOS.prefLabel, Literal("Unique Values")))
        g.add((unique_values_metric, DCTERMS.description, Literal("Number of unique values in the column")))
        g.add((unique_values_metric, DQV.inDimension, DQV.completeness))

        # Unique values measurement
        unique_values_measurement = BNode()
        g.add((unique_values_measurement, RDF.type, DQV.QualityMeasurement))
        g.add((unique_values_measurement, DQV.computedOn, column_uri))
        g.add((unique_values_measurement, DQV.isMeasurementOf, unique_values_metric))
        g.add((unique_values_measurement, DQV.value, Literal(column["unique_values"], datatype=XSD.integer)))

        # Add numerical statistics for continuous columns
        if column["type"] == "continuous" and "mean" in column and column["mean"] is not None:
            # Mean metric
            mean_metric = METRICS.meanValue
            g.add((mean_metric, RDF.type, DQV.Metric))
            g.add((mean_metric, SKOS.prefLabel, Literal("Mean Value")))
            g.add((mean_metric, DCTERMS.description, Literal("Average value of the numerical column")))
            g.add((mean_metric, DQV.inDimension, DQV.accuracy))

            mean_measurement = BNode()
            g.add((mean_measurement, RDF.type, DQV.QualityMeasurement))
            g.add((mean_measurement, DQV.computedOn, column_uri))
            g.add((mean_measurement, DQV.isMeasurementOf, mean_metric))
            g.add((mean_measurement, DQV.value, Literal(column["mean"], datatype=XSD.double)))

            # Standard deviation metric
            if "std" in column and column["std"] is not None:
                std_metric = METRICS.standardDeviation
                g.add((std_metric, RDF.type, DQV.Metric))
                g.add((std_metric, SKOS.prefLabel, Literal("Standard Deviation")))
                g.add((std_metric, DCTERMS.description, Literal("Standard deviation of the numerical column")))
                g.add((std_metric, DQV.inDimension, DQV.accuracy))

                std_measurement = BNode()
                g.add((std_measurement, RDF.type, DQV.QualityMeasurement))
                g.add((std_measurement, DQV.computedOn, column_uri))
                g.add((std_measurement, DQV.isMeasurementOf, std_metric))
                g.add((std_measurement, DQV.value, Literal(column["std"], datatype=XSD.double)))

            # Min/Max values
            if "min" in column and column["min"] is not None:
                min_metric = METRICS.minimumValue
                g.add((min_metric, RDF.type, DQV.Metric))
                g.add((min_metric, SKOS.prefLabel, Literal("Minimum Value")))
                g.add((min_metric, DCTERMS.description, Literal("Minimum value in the numerical column")))
                g.add((min_metric, DQV.inDimension, DQV.accuracy))

                min_measurement = BNode()
                g.add((min_measurement, RDF.type, DQV.QualityMeasurement))
                g.add((min_measurement, DQV.computedOn, column_uri))
                g.add((min_measurement, DQV.isMeasurementOf, min_metric))
                g.add((min_measurement, DQV.value, Literal(column["min"], datatype=XSD.double)))

            if "max" in column and column["max"] is not None:
                max_metric = METRICS.maximumValue
                g.add((max_metric, RDF.type, DQV.Metric))
                g.add((max_metric, SKOS.prefLabel, Literal("Maximum Value")))
                g.add((max_metric, DCTERMS.description, Literal("Maximum value in the numerical column")))
                g.add((max_metric, DQV.inDimension, DQV.accuracy))

                max_measurement = BNode()
                g.add((max_measurement, RDF.type, DQV.QualityMeasurement))
                g.add((max_measurement, DQV.computedOn, column_uri))
                g.add((max_measurement, DQV.isMeasurementOf, max_metric))
                g.add((max_measurement, DQV.value, Literal(column["max"], datatype=XSD.double)))

    # Add provenance information
    quality_assessment = BNode()
    g.add((quality_assessment, RDF.type, PROV.Activity))
    g.add((quality_assessment, RDFS.label, Literal("Dataset Metadata Extraction")))
    g.add((quality_assessment, PROV.startedAtTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
    g.add((quality_assessment, PROV.used, dataset_uri))

    # Add tool information
    tool = DATASET.MetadataExtractionTool
    g.add((tool, RDF.type, PROV.SoftwareAgent))
    g.add((tool, RDFS.label, Literal("Dataset Metadata Extraction Tool")))
    g.add((tool, DCTERMS.description,
           Literal("AI-powered tool for extracting dataset metadata with column descriptions and type classification")))
    g.add((quality_assessment, PROV.wasAssociatedWith, tool))

    # Serialize to Turtle format
    return g.serialize(format='turtle')


def save_dqv_metadata(json_metadata, output_filename):
    """
    Save metadata in DQV format to file

    Args:
        json_metadata (dict): The metadata in JSON format
        output_filename (str): Output filename for DQV file
    """
    dqv_content = create_dqv_metadata(json_metadata)

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(dqv_content)

    return output_filename


def json_to_dqv(json_file_path, output_file_path=None):
    """
    Convert JSON metadata file to DQV format

    Args:
        json_file_path (str): Path to JSON metadata file
        output_file_path (str): Optional output path, if None will use same name with .ttl extension
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_metadata = json.load(f)

    if output_file_path is None:
        output_file_path = json_file_path.replace('.json', '.ttl')

    return save_dqv_metadata(json_metadata, output_file_path)


# Example usage and testing
if __name__ == "__main__":
    # Example metadata for testing
    sample_metadata = {
        "dataset_name": "Customer Analytics Dataset",
        "dataset_description": "Customer transaction data with demographics and purchase history",
        "columns": [
            {
                "name": "customer_id",
                "description": "Unique identifier for each customer",
                "type": "identifier",
                "missing_values": 0,
                "unique_values": 10000
            },
            {
                "name": "age",
                "description": "Customer age in years",
                "type": "continuous",
                "missing_values": 15,
                "unique_values": 45,
                "mean": 34.5,
                "std": 12.3,
                "min": 18,
                "max": 65
            },
            {
                "name": "gender",
                "description": "Customer gender",
                "type": "binary",
                "missing_values": 5,
                "unique_values": 2
            },
            {
                "name": "purchase_category",
                "description": "Product category of the purchase",
                "type": "categorical",
                "missing_values": 0,
                "unique_values": 8
            }
        ]
    }

    # Generate DQV
    dqv_output = create_dqv_metadata(sample_metadata)
    print("Sample DQV Output:")
    print(dqv_output)