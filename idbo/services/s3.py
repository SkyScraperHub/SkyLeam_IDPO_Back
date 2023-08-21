import os
from minio import Minio

S3Clinet = Minio(
            os.getenv("MINIO_STORAGE_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS"),
            secret_key=os.getenv("MINIO_SECRET")
            
        )

class MinioClient:
        
    @staticmethod
    def upload_data(name:str,  data, length = -1):
        S3Clinet.put_object(os.getenv("MINIO_BUCKET_MEDIA"), f'{os.getenv("MINIO_FOLDER")}/{name}',data, length)