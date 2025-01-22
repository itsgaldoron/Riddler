"""Example usage of the Nova Reel service for generating videos from text prompts."""

from riddler.services.video.nova_reel_service import NovaReelService

def main():
    # Initialize the Nova Reel service
    # Replace with your actual S3 bucket URI
    bucket_uri = "s3://korko"
    service = NovaReelService(bucket=bucket_uri)
    
    # Define prompts with their corresponding filenames
    prompts = [
    # Introduction to the Dog Park (0s-4s)
    "Cinematic pan shot of a vibrant anime-style dog park, Kokoro, a lonely Golden Retriever puppy with a fluffy coat and big brown eyes, sits by himself, warm sunlight casting long shadows across the grass, surrounded by other dogs, including a Poodle, a Bulldog, and a Chihuahua. 4k, photorealistic, cinematic quality",
    
    # Kokoro's Isolation (4s-8s)
    "Close-up of Kokoro looking sad and isolated, his ears drooping, as the other dogs, including a playful Beagle and a energetic Labrador, play and run around him, a few clouds drifting lazily across a bright blue sky. Natural lighting, shallow depth of field, 4k",
    
    # Hana's Introduction (8s-12s)
    "Cinematic dolly shot of Hana, a gentle Saint Bernard with a warm smile and a fluffy white coat, approaching Kokoro, toys in her mouth, her tail wagging softly, as the other dogs, including a curious Corgi and a happy Shih Tzu, watch with interest. Photorealistic, 4k, cinematic quality",
    
    # Hana's Kindness (12s-16s)
    "Wide shot of Hana gently dropping a toy in front of Kokoro, Kokoro's eyes lighting up with excitement, as Hana's kind face and warm smile fill the frame, the other dogs, including a friendly Boxer and a lively Dachshund, looking on with curiosity. 4k, photorealistic, cinematic quality",
    
    # Kokoro's Happiness (16s-20s)
    "Close-up of Kokoro playing with the toys, his tail wagging happily, as Hana watches over him with a warm smile, the sun beginning to set behind them, casting a warm glow, and the other dogs, including a sweet Basset Hound and a playful Pug, join in on the fun. Natural lighting, 4k, cinematic quality",
    
    # Kokoro Plays with Hana (20s-24s)
    "Cinematic tracking shot of Kokoro and Hana playing a game of fetch, Kokoro running around the dog park, his ears flapping in the wind, as Hana laughs and cheers him on, the other dogs, including a happy German Shepherd and a lively Australian Shepherd, watching with excitement. 4k, photorealistic, cinematic quality",
    
    # The Parents' Arrival (24s-28s)
    "Cinematic pan shot of Kokoro's parents, Taro, a strong and gentle Golden Retriever, and Yumi, a loving and caring Golden Retriever, arriving at the dog park, looking relieved to see their puppy happy, as Hana greets them with a warm smile, and the other dogs, including a friendly Doberman and a sweet Cocker Spaniel, welcome them to the park. 4k, photorealistic, cinematic quality",
    
    # The Reunion (28s-32s)
    "Wide shot of Kokoro running to his parents, tails wagging, as Hana watches with a warm smile, the family reunited, and the other dogs, including a happy Rottweiler and a lively Shetland Sheepdog, look on with joy. 4k, photorealistic, cinematic quality",
    
    # The Family Leaves the Park (32s-36s)
    "Cinematic dolly shot of the Golden Retriever family leaving the dog park, Kokoro looking back at Hana, who waves goodbye, as the sun sets behind them, casting a warm glow, and the other dogs, including a sweet Afghan Hound and a playful Basenji, wave goodbye. Natural lighting, 4k, cinematic quality",
    
    # The Final Shot (36s-40s)
    "Cinematic close-up of Kokoro looking up at his parents, happy and content, as Hana's kind face and warm smile appear in the background, the camera zooming out to show the family walking off into the distance, surrounded by the other dogs, including a happy Pomeranian and a lively Papillon. 4k, photorealistic, cinematic quality"
]
    
    # Generate videos from the prompts
    service.generate_videos(prompts)

if __name__ == "__main__":
    main() 