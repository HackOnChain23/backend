import openai

from loguru import logger as LOG

from config import DALLE_KEY


def return_image(prompt: str):
    openai.api_key = DALLE_KEY
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=4,
            size="512x512",
        )
        return response
    except Exception:
        LOG.exception(f"Filed to connect with server")
        return "Failed"


# return_image("cute cat")
