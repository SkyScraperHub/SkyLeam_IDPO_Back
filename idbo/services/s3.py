import os
from minio import Minio
from datetime import timedelta
S3Clinet = Minio(
            os.getenv("MINIO_STORAGE_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS"),
            secret_key=os.getenv("MINIO_SECRET"),
            secure=False
            
        )

class MinioClient:
        
    @staticmethod
    def upload_data(name:str,  data, length = -1, num_parallel_uploads = 3):
        S3Clinet.put_object(os.getenv("MINIO_BUCKET_MEDIA"), name, data, length, num_parallel_uploads= num_parallel_uploads, part_size=10*1024*1024)
        
        
    @staticmethod
    def get_presigned_url(name: str):
        return S3Clinet.presigned_get_object(os.getenv("MINIO_BUCKET_MEDIA"), name, expires=timedelta(hours = 1))
    
    @staticmethod
    def delete_object(name: str):
        S3Clinet.remove_object(os.getenv("MINIO_BUCKET_MEDIA"), name)
    
    @staticmethod
    def get_public_url(name):
        url = os.getenv("MINIO_STORAGE_ENDPOINT")
        bucket = os.getenv("MINIO_BUCKET_MEDIA")
        return f"https://{url}/{bucket}/{name}"

