"""
MinIO Service for File Storage
"""
from minio import Minio
from minio.error import S3Error
from typing import Optional, BinaryIO
from app.config import settings
from app.utils.logger import logger
import io


class MinIOService:
    """Service for MinIO (S3-compatible) file storage"""
    
    _client: Optional[Minio] = None
    
    @classmethod
    def get_client(cls) -> Minio:
        """Get MinIO client (singleton)"""
        if cls._client is None:
            try:
                endpoint = settings.MINIO_ENDPOINT.split(':')[0]
                port = int(settings.MINIO_ENDPOINT.split(':')[1]) if ':' in settings.MINIO_ENDPOINT else 9000
                
                cls._client = Minio(
                    endpoint,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_USE_SSL
                )
                
                # Ensure bucket exists
                if not cls._client.bucket_exists(settings.MINIO_BUCKET_NAME):
                    cls._client.make_bucket(settings.MINIO_BUCKET_NAME)
                    logger.info(f"Created bucket: {settings.MINIO_BUCKET_NAME}")
                
                logger.info("MinIO connection established")
            except Exception as e:
                logger.error(f"MinIO connection failed: {e}")
                raise
        return cls._client
    
    @classmethod
    def upload_file(
        cls,
        file_path: str,
        file_data: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload file to MinIO"""
        client = cls.get_client()
        
        try:
            client.put_object(
                settings.MINIO_BUCKET_NAME,
                file_path,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
            logger.info(f"File uploaded", path=file_path)
            return file_path
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    @classmethod
    def download_file(cls, file_path: str) -> bytes:
        """Download file from MinIO"""
        client = cls.get_client()
        
        try:
            response = client.get_object(settings.MINIO_BUCKET_NAME, file_path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise
    
    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        """Delete file from MinIO"""
        client = cls.get_client()
        
        try:
            client.remove_object(settings.MINIO_BUCKET_NAME, file_path)
            logger.info(f"File deleted", path=file_path)
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    @classmethod
    def get_file_url(cls, file_path: str, expires_in_seconds: int = 3600) -> str:
        """Get presigned URL for file access"""
        client = cls.get_client()
        
        try:
            url = client.presigned_get_object(
                settings.MINIO_BUCKET_NAME,
                file_path,
                expires=expires_in_seconds
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
