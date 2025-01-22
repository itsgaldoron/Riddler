import boto3
import os
from typing import List

def download_mp4_files(bucket_name: str, output_dir: str = "downloads") -> List[str]:
    """
    Downloads all MP4 files from the specified S3 bucket.
    
    Args:
        bucket_name (str): The name of the S3 bucket (without s3:// prefix)
        output_dir (str): Local directory to save downloaded files
        
    Returns:
        List[str]: List of downloaded file paths
    """
    # Create S3 client
    s3_client = boto3.client('s3')
    
    # Create output directory if it doesn't exist
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_files = []
    
    try:
        # List all objects in the bucket
        paginator = s3_client.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' not in page:
                continue
                
            for obj in page['Contents']:
                key = obj['Key']
                
                # Only download MP4 files
                if key.lower().endswith('.mp4'):
                    # Get the parent folder name and use it in the filename
                    folder_name = os.path.dirname(key)
                    if folder_name:
                        local_filename = f"{os.path.basename(folder_name)}_output.mp4"
                    else:
                        local_filename = os.path.basename(key)
                    
                    # Create the local file path
                    local_file_path = os.path.join(output_dir, local_filename)
                    
                    # Download the file
                    print(f"Downloading {key} to {local_file_path}...")
                    s3_client.download_file(bucket_name, key, local_file_path)
                    downloaded_files.append(local_file_path)
                    
        return downloaded_files
        
    except Exception as e:
        print(f"Error downloading files: {str(e)}")
        return downloaded_files

if __name__ == "__main__":
    # Extract bucket name from ARN
    bucket_arn = "arn:aws:s3:::anime-dog"
    bucket_name = bucket_arn.split(":")[-1]
    
    # Download the files
    downloaded = download_mp4_files(bucket_name)
    
    if downloaded:
        print("\nFull paths of downloaded files:")
        for file in downloaded:
            print(f"- {file}")
            
        # Also print the parent directory
        if downloaded:
            print(f"\nAll files are in directory: {os.path.dirname(downloaded[0])}")
    else:
        print("\nNo MP4 files were downloaded.") 