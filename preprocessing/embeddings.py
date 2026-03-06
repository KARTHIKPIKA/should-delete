from functools import lru_cache  # stores results of expensive function calls Same input → returns cached result instead of recomputing
from PIL import Image # PIL (Pillow) — Python's image library Used to open and read image files before sending to AI
from tenacity import ( # Tenacity = a retry library — automatically retries failed API calls
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tqdm import tqdm
from voyageai import Client
from voyageai.error import (
    ServiceUnavailableError,
    TryAgain,
    Timeout,
    RateLimitError,
    ServerError,
)


RETRY_EXCEPTIONS = (
    ServiceUnavailableError,
    TryAgain,
    Timeout,
    RateLimitError,
    ServerError,
)


# Attempt 1 fails → wait 1s ; Attempt 2 fails → wait 2s ; Attempt 3 fails → raise error (NO wait, just give up)
def voyageai_retry():
    """
    A helper decorator to standardize retry policies for VoyageAI operations.
    """
    return retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_exception_type(RETRY_EXCEPTIONS),
    )


# Creates VoyageAI client once and caches it Every subsequent call returns the same client instance
@lru_cache()
def get_client():
    return Client()


@voyageai_retry()
@lru_cache()
def generate_embedding(input_type, image_path=None, text=None):
    """Generate embedding for images or text query using VoyageAI"""

    if image_path is not None and text is not None:
        raise ValueError("Only one of image_path or text should be provided.")

    if image_path is None and text is None:
        raise ValueError("Either image_path or text should be provided.")

    client = get_client()

    if image_path is not None:
        input = Image.open(image_path)
    else:
        input = text

    response = client.multimodal_embed(
        inputs=[[input]],
        model="voyage-multimodal-3",
        input_type=input_type,
    )

    return response.embeddings[0]


def generate_embeddings_in_batch(input_type, image_paths):
    """Generate embedding for images in batches of 50, using VoyageAI"""

    embeddings = []
    for i in tqdm(range(0, len(image_paths), 50)):
        batch = image_paths[i : i + 50]
        embeddings.extend(generate_embedding(input_type, batch))

    return embeddings
