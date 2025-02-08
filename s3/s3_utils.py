import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
import dotenv

dotenv.load_dotenv()
BUCKET_NAME = os.getenv('BUCKET_NAME')


def upload_file_to_s3(directory_path, local_filename, s3_filename, bucket=BUCKET_NAME):
    """Upload a file to S3 bucket
    Args:
        directory_path: Path to directory containing the file
        local_filename: Name of the file to upload
        s3_filename: Desired name in S3 (e.g. 'recordings/file.m4a')
        bucket: S3 bucket name (defaults to BUCKET_NAME from env)
    """
    s3 = boto3.client('s3')
    local_file_path = os.path.join(directory_path, local_filename)
    
    try:
        s3.upload_file(local_file_path, bucket, s3_filename)
        print(f"File '{local_filename}' uploaded to bucket '{bucket}' as '{s3_filename}'.")
        return True
    except FileNotFoundError:
        print("The file was not found.")
    except NoCredentialsError:
        print("Credentials not available.")
    except ClientError as e:
        print(f"An error occurred: {e}")
    return False


def download_file_from_s3(directory_path, local_filename, s3_filename, bucket=BUCKET_NAME):
    """Download a file from S3 bucket
    Args:
        directory_path: Path where to save the downloaded file
        local_filename: Desired name for the downloaded file
        s3_filename: Name of file in S3 (e.g. 'recordings/file.m4a')
        bucket: S3 bucket name (defaults to BUCKET_NAME from env)
    """
    s3 = boto3.client('s3')
    local_file_path = os.path.join(directory_path, local_filename)
    
    try:
        s3.download_file(bucket, s3_filename, local_file_path)
        print(f"File '{s3_filename}' from bucket '{bucket}' downloaded as '{local_filename}'.")
        return True
    except FileNotFoundError:
        print("The local path was not found.")
    except NoCredentialsError:
        print("Credentials not available.")
    except ClientError as e:
        print(f"An error occurred: {e}")
    return False


# Example usage
local_storage_dir = "temp"
directory_path = os.path.join(os.path.dirname(__file__), local_storage_dir)
local_filename = "test.m4a"
s3_file_dir = "recordings"
s3_filename = "test.m4a"

# Construct S3 path by joining directory and filename
s3_full_path = f"{s3_file_dir}/{s3_filename}"

# Upload
upload_file_to_s3(directory_path, local_filename, s3_full_path)

# Download - using a different local filename for the downloaded file
download_file_from_s3(directory_path, f"downloaded_{local_filename}", s3_full_path)
