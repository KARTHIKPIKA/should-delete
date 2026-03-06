import base64
from langfuse.openai import AsyncOpenAI
from openai import BadRequestError
from ratelimit import limits, sleep_and_retry
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

import json

from config import OPENAI_MAX_REQUESTS_PER_MINUTE

async_client = AsyncOpenAI()


@sleep_and_retry
@limits(calls=OPENAI_MAX_REQUESTS_PER_MINUTE, period=1)
@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_fixed(2),  # Wait 2 seconds between retries
    retry=retry_if_exception_type(BadRequestError),
)
async def call_openai_async(
    model,
    messages=None,
    convert_json_answer_to_dict=False,
    **kwargs,
):
    response = await async_client.chat.completions.create(
        model=model, messages=messages, **kwargs
    )
    answer = response.choices[0].message.content
    if convert_json_answer_to_dict:
        answer = json.loads(answer)
    return answer


def image_to_base64(image_path):
    """
    Converts a PIL image to a Base64 encoded string.

    :param image_path: Path to the PNG image file
    :return: Base64 encoded string
    """
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_string
