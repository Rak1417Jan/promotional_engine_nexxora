"""
Export Service for Data Export
"""
import pandas as pd
import json
from typing import Dict, Any, List, Optional
from app.services.mongodb_service import MongoDBService
from app.utils.logger import logger


class ExportService:
    """Service for exporting data to various formats"""
    
    @staticmethod
    def export_from_mongodb(
        operator_id: int,
        entity_type: str,
        export_format: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> str:
        """Export data from MongoDB to file"""
        collection_name = f"{entity_type}s"  # e.g., "players", "games"
        
        # Build filter query
        filter_query = {}
        if filters:
            # Convert filters to MongoDB query
            for key, value in filters.items():
                if key.startswith("data."):
                    # Filter on data fields
                    filter_query[key] = value
                else:
                    filter_query[key] = value
        
        # Fetch documents
        if limit:
            documents = MongoDBService.find_documents(
                collection_name,
                operator_id,
                filter_query,
                limit=limit
            )
        else:
            documents = MongoDBService.find_documents(
                collection_name,
                operator_id,
                filter_query,
                limit=100000  # Large limit
            )
        
        # Extract data from documents
        records = []
        for doc in documents:
            record = doc.get("data", {})
            record["_id"] = str(doc.get("_id"))
            record["external_id"] = doc.get("external_id")
            records.append(record)
        
        # Convert to requested format
        if export_format == "json":
            return json.dumps(records, indent=2, default=str)
        elif export_format == "csv":
            df = pd.DataFrame(records)
            return df.to_csv(index=False)
        elif export_format == "excel":
            df = pd.DataFrame(records)
            # Return as bytes for Excel
            from io import BytesIO
            output = BytesIO()
            df.to_excel(output, index=False)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    @staticmethod
    def save_export_file(
        file_path: str,
        content: str,
        export_format: str
    ) -> int:
        """Save export content to file"""
        try:
            if export_format == "excel":
                # Content is already bytes
                with open(file_path, 'wb') as f:
                    f.write(content)
                file_size = len(content)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                file_size = len(content.encode('utf-8'))
            
            logger.info(f"Export file saved", path=file_path, size=file_size)
            return file_size
        except Exception as e:
            logger.error(f"Error saving export file: {e}")
            raise
