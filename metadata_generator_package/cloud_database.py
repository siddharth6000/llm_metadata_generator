"""
Cloud Database Manager for Supabase integration.

Handles dataset metadata storage, file uploads, and database operations
for persistent cloud storage of analysis results.
"""

import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from supabase import create_client, Client
    from postgrest.exceptions import APIError
    from storage3.exceptions import StorageException
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class CloudDatabaseManager:
    """Cloud Database Manager for Supabase integration."""

    def __init__(self, supabase_url: str, supabase_key: str):
        self.client: Client = create_client(supabase_url, supabase_key)
        self.bucket_name = "dataset-metadata"
        print(f"CloudDatabaseManager initialized")

    def save_dataset_metadata(self, session_id: str, metadata: Dict[str, Any],
                            zip_file_path: str, original_filename: str,
                            zip_download_filename: str = None) -> Dict[str, Any]:
        """Save dataset metadata and ZIP file to cloud database."""
        # Validate inputs
        if not all([session_id, metadata, zip_file_path, original_filename]):
            return {"success": False, "error": "Missing required parameters"}

        if not os.path.exists(zip_file_path):
            return {"success": False, "error": f"ZIP file not found: {zip_file_path}"}

        file_size = os.path.getsize(zip_file_path)
        if file_size == 0:
            return {"success": False, "error": "ZIP file is empty"}

        try:
            # Generate unique identifiers
            file_id = str(uuid.uuid4())
            dataset_name = metadata.get('dataset_name', 'dataset')
            clean_filename = self._create_clean_filename(dataset_name)
            storage_filename = f"{clean_filename[:-4]}_{file_id}.zip"
            storage_path = f"datasets/{storage_filename}"

            self._log(f"Storing as: {clean_filename} (internal: {storage_filename})")

            # Upload file to storage
            with open(zip_file_path, 'rb') as file:
                self.client.storage.from_(self.bucket_name).upload(
                    path=storage_path,
                    file=file,
                    file_options={"content-type": "application/zip", "upsert": "true"}
                )

            file_url = self.client.storage.from_(self.bucket_name).get_public_url(storage_path)

            # Prepare metadata record
            metadata_record = {
                "file_id": file_id,
                "session_id": session_id,
                "dataset_name": metadata.get('dataset_name', 'Unknown Dataset'),
                "dataset_description": metadata.get('dataset_description', 'No description'),
                "original_filename": original_filename,
                "zip_filename": clean_filename,
                "column_count": len(metadata.get('columns', [])),
                "metadata_json": metadata,
                "file_url": file_url,
                "storage_path": storage_path,
                "file_size": file_size,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Insert to database
            result = self.client.table('dataset_metadata').insert(metadata_record).execute()

            if result.data:
                self._log(f"Dataset saved: {file_id} as {clean_filename}")
                return {
                    "success": True,
                    "file_id": file_id,
                    "file_url": file_url,
                    "storage_path": storage_path,
                    "storage_filename": storage_filename,
                    "zip_filename": clean_filename,
                    "file_size": file_size
                }
            else:
                return {"success": False, "error": "Database insert failed"}

        except StorageException as e:
            return self._handle_error("Storage upload", e)
        except APIError as e:
            return self._handle_error("Database insert", e)
        except Exception as e:
            return self._handle_error("Save operation", e)

    def get_dataset_list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of datasets from cloud database."""
        try:
            result = self.client.table('dataset_metadata').select(
                'file_id, dataset_name, dataset_description, original_filename, '
                'zip_filename, column_count, file_size, created_at, updated_at'
            ).order('created_at', desc=True).limit(limit).execute()

            return result.data if result.data else []
        except Exception as e:
            self._log(f"Error fetching dataset list: {e}", True)
            return []

    def get_dataset_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get specific dataset metadata by file ID."""
        try:
            result = self.client.table('dataset_metadata').select('*').eq('file_id', file_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self._log(f"Error fetching dataset {file_id}: {e}", True)
            return None

    def delete_dataset(self, file_id: str) -> bool:
        """Delete dataset from cloud database and storage."""
        try:
            # Get storage path
            dataset = self.get_dataset_metadata(file_id)
            if not dataset:
                return False

            # Delete from storage
            storage_path = dataset.get('storage_path')
            if storage_path:
                try:
                    self.client.storage.from_(self.bucket_name).remove([storage_path])
                except Exception as e:
                    self._log(f"Storage deletion failed: {e}", True)

            # Delete from database
            result = self.client.table('dataset_metadata').delete().eq('file_id', file_id).execute()

            if result.data:
                self._log(f"Dataset deleted: {file_id}")
                return True
            return False

        except Exception as e:
            self._log(f"Error deleting dataset {file_id}: {e}", True)
            return False

    def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        try:
            result = self.client.table('dataset_metadata').select('file_size').execute()

            if result.data:
                total_files = len(result.data)
                total_size_bytes = sum(row.get('file_size', 0) for row in result.data)
                total_size_mb = round(total_size_bytes / (1024 * 1024), 2)
            else:
                total_files = total_size_bytes = total_size_mb = 0

            return {
                'total_files': total_files,
                'total_size_bytes': total_size_bytes,
                'total_size_mb': total_size_mb,
                'bucket_name': self.bucket_name
            }

        except Exception as e:
            self._log(f"Error calculating storage usage: {e}", True)
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'bucket_name': self.bucket_name,
                'error': str(e)
            }

    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for database and storage connections."""
        health_status = {
            'database_connection': False,
            'storage_connection': False,
            'bucket_exists': False,
            'overall_health': False,
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Test database
            self.client.table('dataset_metadata').select('count').limit(1).execute()
            health_status['database_connection'] = True

            # Test storage
            buckets = self.client.storage.list_buckets()
            health_status['storage_connection'] = True
            health_status['bucket_exists'] = any(bucket.name == self.bucket_name for bucket in buckets)

            # Overall health
            health_status['overall_health'] = all([
                health_status['database_connection'],
                health_status['storage_connection'],
                health_status['bucket_exists']
            ])

        except Exception as e:
            health_status['error'] = str(e)

        return health_status

    # Private helper methods

    def _log(self, message: str, is_error: bool = False):
        """Simple logging helper with consistent formatting."""
        prefix = "❌" if is_error else "✅"
        print(f"{prefix} {message}")

    def _handle_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Unified error handling with logging."""
        error_msg = f"{operation} failed: {error}"
        self._log(error_msg, True)
        return {"success": False, "error": str(error)}

    def _create_clean_filename(self, dataset_name: str) -> str:
        """Create a clean filename from dataset name."""
        if not dataset_name:
            return "dataset_package.zip"

        # Clean the dataset name - remove special characters, replace spaces with underscores
        import re
        clean_name = re.sub(r'[^\w\s-]', '', dataset_name)  # Remove special chars except spaces and hyphens
        clean_name = re.sub(r'[-\s]+', '_', clean_name)     # Replace spaces and hyphens with underscores
        clean_name = clean_name.strip('_').lower()          # Remove leading/trailing underscores, lowercase

        # Ensure we have a valid filename
        if not clean_name:
            clean_name = "dataset"

        return f"{clean_name}_package.zip"