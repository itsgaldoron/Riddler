"""
Service for generating videos using Amazon Bedrock's Nova Reel model.
This service provides functionality to generate videos from text prompts using Amazon's Nova Reel model.
"""

import json
import time
import uuid
import boto3
import requests as req
import botocore.session
import os

from botocore.auth import SigV4Auth
from typing import Dict, List, Tuple, Optional, Union
from botocore.awsrequest import AWSRequest

class NovaReelService:
    """Service for generating videos using Amazon Bedrock's Nova Reel model."""
    
    SERVICE_NAME: str = 'bedrock'
    MAX_TIME: int = 3600
    
    def __init__(self, bucket: str = None, region: str = 'us-east-1', model_id: str = 'amazon.nova-reel-v1:0'):
        """
        Initialize the Nova Reel service.
        
        Args:
            bucket: S3 bucket name to use (without s3:// prefix)
            region: AWS region to use
            model_id: Nova Reel model ID
        """
        self.region = region
        self.model_id = model_id
        # Use provided bucket or generate unique name
        self.bucket = bucket if bucket else f"nova-reel-videos-{str(uuid.uuid4())[:8]}"
        self.local_output_dir = f"./{self.bucket}"
        os.makedirs(self.local_output_dir, exist_ok=True)

    def get_inference(self, prompt_id: int, payload: Dict) -> Optional[Tuple[int, Dict]]:
        """
        Make an inference request to the Nova Reel model.
        
        Args:
            prompt_id: ID of the prompt being processed
            payload: Request payload containing the prompt and configuration
            
        Returns:
            Tuple of (prompt_id, response) if successful, None otherwise
        """
        print(f"Making an inference request to {self.model_id}, payload={payload}")
        try:
            endpoint: str = f"https://{self.SERVICE_NAME}-runtime.{self.region}.amazonaws.com/async-invoke"
            print(endpoint)

            request_body = json.dumps(payload)
            print(json.dumps(payload, indent=2))

            request = AWSRequest(
                method='POST',
                url=endpoint,
                data=request_body,
                headers={'content-type': 'application/json'}
            )

            session = botocore.session.Session()
            sigv4 = SigV4Auth(session.get_credentials(), self.SERVICE_NAME, self.region)
            sigv4.add_auth(request)

            prepped = request.prepare()
            response = req.post(prepped.url, headers=prepped.headers, data=request_body)

            if response.status_code == 200:
                return (prompt_id, response.json())
            else:
                print(f"Error: Received status code {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            print(f"Exception occurred: {e}")
            return None

    def print_async_job_status(self, arn: str, filename: str = None) -> str:
        """
        Check and print the status of an async job.
        
        Args:
            arn: The ARN of the job to check
            filename: Custom filename for the output video
            
        Returns:
            The status of the job
        """
        bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region)
        invocation = bedrock_runtime.get_async_invoke(invocationArn=arn)

        print(json.dumps(invocation, indent=2, default=str))

        invocation_arn = invocation["invocationArn"]
        status = invocation["status"]
        
        if status == "Completed":
            bucket_uri = invocation["outputDataConfig"]["s3OutputDataConfig"]["s3Uri"]
            video_uri = f"{bucket_uri}/{filename if filename else 'output.mp4'}"
            print(f"Video is available at: {video_uri}")
        elif status == "InProgress":
            start_time = invocation["submitTime"]
            print(f"Job {invocation_arn} is in progress. Started at: {start_time}")
        elif status == "Failed":
            failure_message = invocation["failureMessage"]
            print(f"Job {invocation_arn} failed. Failure message: {failure_message}")
            
        return status

    def create_payload(self, prompt: str, filename: str = None) -> Dict:
        """
        Create a payload for the Nova Reel model request.
        
        Args:
            prompt: Text prompt to generate video from
            filename: Custom filename for the output video
            
        Returns:
            Dictionary containing the request payload
        """
        s3_uri = f"s3://{self.bucket}"
        if filename:
            # Remove .mp4 extension if present and add it back to ensure consistency
            base_filename = filename.replace('.mp4', '')
            s3_uri = f"s3://{self.bucket}/{base_filename}.mp4"

        return {
            "modelId": self.model_id,
            "modelInput": {
                "taskType": "TEXT_VIDEO",
                "textToVideoParams": {
                    "text": prompt
                },
                "videoGenerationConfig": {
                    "durationSeconds": 6,
                    "fps": 24,
                    "dimension": "1280x720",
                    "seed": 0
                }
            },
            "outputDataConfig": {
                "s3OutputDataConfig": {
                    "s3Uri": s3_uri
                }
            },
            "clientRequestToken": str(uuid.uuid4())
        }

    def download_video(self, s3_uri: str, sequence_number: int) -> str:
        """
        Download video from S3 to local storage with sequential naming.
        
        Args:
            s3_uri: S3 URI of the video
            sequence_number: Sequence number for the video
            
        Returns:
            Local file path of the downloaded video
        """
        s3 = boto3.client('s3')
        bucket_name = s3_uri.split('/')[2]
        key = '/'.join(s3_uri.split('/')[3:])
        
        # Create sequential filename
        local_path = f"{self.local_output_dir}/video_{sequence_number:03d}.mp4"
        
        try:
            s3.download_file(bucket_name, key, local_path)
            print(f"Downloaded video to {local_path}")
            return local_path
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None

    def generate_videos(self, prompts: Union[List[str], List[Tuple[str, str]]]) -> None:
        """
        Generate videos from a list of text prompts.
        
        Args:
            prompts: List of text prompts or tuples of (prompt, filename) to generate videos from
        """
        print(f"Going to make {len(prompts)} requests")
        
        # Handle both simple prompts and prompt+filename tuples
        formatted_prompts = []
        for i, prompt in enumerate(prompts):
            if isinstance(prompt, tuple):
                prompt_text, filename = prompt
                formatted_prompts.append((i, self.create_payload(prompt_text, filename), filename))
            else:
                formatted_prompts.append((i, self.create_payload(prompt), None))
        
        # Make inference requests
        start_time = time.perf_counter()
        responses = [self.get_inference(prompt[0], prompt[1]) for prompt in formatted_prompts]
        elapsed_time = time.perf_counter() - start_time
        print(f"Total time taken for {len(prompts)} calls made: {elapsed_time:.2f} seconds")

        # Extract invocation ARNs and filenames
        invocation_data = []
        for r, prompt_info in zip(responses, formatted_prompts):
            if r:  # Only process successful responses
                print(f"response={r}")
                invocation_data.append((r[1]['invocationArn'], prompt_info[2]))

        # Monitor job status
        jobs_total = len(invocation_data)
        jobs_completed = 0
        st = time.time()
        bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region)
        
        while True:
            jobs_completed = 0  # Reset counter for each iteration
            for i, (arn, filename) in enumerate(invocation_data):
                invocation = bedrock_runtime.get_async_invoke(invocationArn=arn)
                status = invocation["status"]
                print(f"arn={arn}, filename={filename}, status={status}")
                
                if status == "Completed":
                    jobs_completed += 1
                    # Get the video URI from the completed job
                    bucket_uri = invocation["outputDataConfig"]["s3OutputDataConfig"]["s3Uri"]
                    video_uri = f"{bucket_uri}/{filename if filename else 'output.mp4'}"
                    # Download the video with sequential numbering
                    self.download_video(video_uri, i)
                    
            if jobs_completed == jobs_total:
                print("All jobs completed, exiting")
                break
                
            if time.time() - st > self.MAX_TIME:
                print(f"{self.MAX_TIME}s elapsed but seems like all jobs are still not completed, exiting")
                break
                
            time.sleep(60)
            
        print("All done") 