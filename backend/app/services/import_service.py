"""
Import Service for Data Import
"""
import pandas as pd
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from app.utils.logger import logger
from app.services.mongodb_service import MongoDBService


class ImportService:
    """Service for importing data from various formats"""
    
    @staticmethod
    def detect_schema(file_path: str, file_format: str, sample_size: int = 100) -> Dict[str, Any]:
        """Detect schema from file"""
        try:
            if file_format == "csv":
                df = pd.read_csv(file_path, nrows=sample_size)
            elif file_format == "excel":
                df = pd.read_excel(file_path, nrows=sample_size)
            elif file_format == "json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        df = pd.DataFrame(data[:sample_size])
                    else:
                        raise ValueError("JSON must be an array of objects")
            else:
                raise ValueError(f"Unsupported format: {file_format}")
            
            schema = {
                "fields": {},
                "indexes": [],
                "validation_rules": {}
            }
            
            for col in df.columns:
                # Infer type
                dtype = str(df[col].dtype)
                if 'int' in dtype:
                    field_type = "integer"
                elif 'float' in dtype:
                    field_type = "number"
                elif 'bool' in dtype:
                    field_type = "boolean"
                elif 'datetime' in dtype:
                    field_type = "datetime"
                else:
                    field_type = "string"
                
                schema["fields"][col] = {
                    "type": field_type,
                    "required": not df[col].isna().all(),
                    "indexed": False
                }
            
            return schema
        except Exception as e:
            logger.error(f"Error detecting schema: {e}")
            raise
    
    @staticmethod
    def parse_file(
        file_path: str,
        file_format: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Parse file and return list of records"""
        records = []
        
        try:
            if file_format == "csv":
                df = pd.read_csv(file_path)
                records = df.to_dict('records')
            elif file_format == "excel":
                df = pd.read_excel(file_path)
                records = df.to_dict('records')
            elif file_format == "json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        records = data
                    else:
                        records = [data]
            elif file_format == "xml":
                tree = ET.parse(file_path)
                root = tree.getroot()
                # Simple XML to dict conversion
                for item in root:
                    record = {}
                    for child in item:
                        record[child.tag] = child.text
                    records.append(record)
            else:
                raise ValueError(f"Unsupported format: {file_format}")
            
            # Validate against schema if provided
            if schema:
                records = ImportService._validate_records(records, schema)
            
            return records
        except Exception as e:
            logger.error(f"Error parsing file: {e}")
            raise
    
    @staticmethod
    def _validate_records(records: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate records against schema"""
        validated = []
        fields = schema.get("fields", {})
        
        for record in records:
            valid = True
            for field_name, field_def in fields.items():
                if field_def.get("required", False) and field_name not in record:
                    valid = False
                    break
            if valid:
                validated.append(record)
        
        return validated
    
    @staticmethod
    def import_to_mongodb(
        operator_id: int,
        entity_type: str,
        records: List[Dict[str, Any]],
        schema_version: int = 1,
        external_id_field: str = "id"
    ) -> Tuple[int, int]:
        """Import records to MongoDB"""
        collection_name = f"{entity_type}s"  # e.g., "players", "games"
        
        # Prepare documents
        documents = []
        for record in records:
            external_id = str(record.get(external_id_field, f"auto_{len(documents)}"))
            
            document = {
                "operator_id": operator_id,
                "external_id": external_id,
                "schema_version": schema_version,
                "data": record,
                "metadata": {
                    "created_at": None,
                    "updated_at": None
                }
            }
            documents.append(document)
        
        # Bulk insert
        try:
            inserted_count = MongoDBService.bulk_insert(collection_name, documents)
            failed_count = len(records) - inserted_count
            return inserted_count, failed_count
        except Exception as e:
            logger.error(f"Error importing to MongoDB: {e}")
            raise
