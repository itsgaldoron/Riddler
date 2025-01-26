"""Example usage of Nova Reel for creating trending YouTube Shorts content."""

from riddler.services.video.nova_reel_service import NovaReelService
import uuid
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def create_s3_bucket(bucket_name: str, region: str = 'us-east-1') -> bool:
    """
    Create an S3 bucket with the specified name.
    
    Args:
        bucket_name: Name of the bucket to create
        region: AWS region to create the bucket in
        
    Returns:
        True if bucket was created successfully, False otherwise
    """
    try:
        s3 = boto3.client('s3', region_name=region)
        if region != 'us-east-1':
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        else:
            s3.create_bucket(Bucket=bucket_name)
        print(f"Successfully created bucket: {bucket_name}")
        return True
    except ClientError as e:
        print(f"Error creating bucket: {e}")
        return False
    except NoCredentialsError:
        print("AWS credentials not found")
        return False

def main():
    # Generate random bucket name
    bucket_name = f"nova-reel-{str(uuid.uuid4())[:8]}"
    bucket_uri = f"s3://{bucket_name}"
    
    # Create the bucket first
    if not create_s3_bucket(bucket_name):
        print("Failed to create bucket, exiting...")
        return
        
    # Initialize Nova Reel service with the created bucket
    service = NovaReelService(bucket=bucket_name)
    
    # Prompts based on trending YouTube Shorts categories
    prompts =[
    "Hyper-realistic close-up of a veiny, throbbing banana with glistening 'foreskin' tip thrusting rapidly into a juicy, split watermelon, pulsating with each aggressive penetration, droplets flying, dynamic camera angles emphasizing the obscene fruit nudity, fast-paced editing, no slow motion.", 
    "Two hairy kiwifruits with swollen, bouncing flesh mimicking testicles slapping against a curvaceous peach's cleft, hyper-detailed texture of fuzz and juices, rapid back-and-forth motion, camera circling the explicit action, frenetic energy.",
    "A cluster of engorged grapes violently squeezed between two cantaloupe 'buttocks', bursting with sticky liquid as a phallic pineapple rams repeatedly into the dripping mess, extreme close-ups on penetrating fruit flesh, frenzied rhythm.",
    "Thick avocado pit plunging in/out of a overripe fig's gaping opening, wrinkled skin stretching with each thrust, seeds oozing, camera shaking with intensity, rapid-fire penetration sequences under sticky lighting.",
    "Multiple bananas with glistening peels forming an orgy - one pistoning into a honeydew's cleft while others rub against mango 'breasts', juices spraying in slow arcs, chaotic multi-angle shots at breakneck speed.",
    "A pulsating pomegranate bursting bloody seeds rhythmically onto trembling lychee 'nipples', followed by a zucchini violently splitting the fruit open, high-speed photography capturing every vulgar splash.",
    "Close-up of a hairy coconut 'anus' being aggressively penetrated by a rotating pineapple crown, fibrous textures ripping, milk spraying in arcs, ultra-fast drilling motion with dynamic camera rotations around the obscene act."
]
    
    print(f"Using bucket: {bucket_uri}")
    
    # Generate videos from prompts
    service.generate_videos(prompts)

if __name__ == "__main__":
    main() 