"""
S3-compatible storage service
"""

import logging
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
import aiohttp
import asyncio
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class S3Service:
    """S3-compatible storage service"""
    
    def __init__(self, settings):
        self.endpoint_url = settings.s3_endpoint_url
        self.region = settings.s3_region
        self.bucket = settings.s3_bucket
        self.public_base_url = settings.s3_public_base_url
        
        # Create S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key
        )
    
    async def generate_presigned_upload_url(
        self,
        file_key: str,
        filename: str,
        expires_in: int = 3600
    ) -> str:
        """Generate presigned URL for file upload"""
        try:
            # Generate presigned URL for PUT request
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': file_key,
                    'ContentType': 'application/pdf'
                },
                ExpiresIn=expires_in
            )
            
            logger.info(f"Generated presigned URL for {file_key}")
            return presigned_url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    async def download_file(self, file_url: str) -> bytes:
        """Download file from S3"""
        try:
            # Parse URL to get key
            parsed_url = urlparse(file_url)
            file_key = parsed_url.path.lstrip('/')
            
            # Download file
            response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=file_key
            )
            
            file_content = response['Body'].read()
            logger.info(f"Downloaded file {file_key} ({len(file_content)} bytes)")
            
            return file_content
            
        except ClientError as e:
            logger.error(f"Failed to download file {file_url}: {e}")
            raise
    
    async def upload_file(self, file_data: bytes, file_key: str, content_type: str = 'application/pdf') -> str:
        """Upload file directly to S3 (server-side upload)"""
        try:
            # Upload file
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=file_key,
                Body=file_data,
                ContentType=content_type
            )
            
            # Generate public URL
            public_url = self.get_public_url(file_key)
            
            logger.info(f"Uploaded file {file_key} ({len(file_data)} bytes)")
            return public_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file {file_key}: {e}")
            raise
    
    async def upload_preview_image(self, image_data: bytes, image_key: str) -> str:
        """Upload preview image to S3"""
        try:
            # Upload image
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=image_key,
                Body=image_data,
                ContentType='image/png'
            )
            
            # Generate public URL
            public_url = self.get_public_url(image_key)
            
            logger.info(f"Uploaded preview image {image_key}")
            return public_url
            
        except ClientError as e:
            logger.error(f"Failed to upload preview image {image_key}: {e}")
            raise
    
    def get_public_url(self, file_key: str) -> str:
        """Get public URL for file"""
        if self.public_base_url:
            return f"{self.public_base_url.rstrip('/')}/{file_key}"
        else:
            # Fallback to S3 URL
            return f"{self.endpoint_url.rstrip('/')}/{self.bucket}/{file_key}"
    
    async def file_exists(self, file_key: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket,
                Key=file_key
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    async def delete_file(self, file_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=file_key
            )
            
            logger.info(f"Deleted file {file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file {file_key}: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> list:
        """List files in S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return files
            
        except ClientError as e:
            logger.error(f"Failed to list files: {e}")
            return []
