import openai

from aiohttp import ClientSession
from loguru import logger as LOG

from config import DALLE_API_KEY, NFT_STORAGE_API_KEY


class Dalle:
    def __init__(self):
        self.ipfs_key = NFT_STORAGE_API_KEY
        openai.api_key = DALLE_API_KEY

    async def generate_image(self, prompt: str, quantity: int):
        if quantity > 4:
            err = f"{quantity}?? Too much."
            LOG.error(err)
            raise Exception(err)
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=quantity,
                size="512x512",
            )
            return [image["url"] for image in response["data"]]
        except Exception:
            LOG.exception(f"Failed while generating images by DALL-E")
            return []

    async def download_image(self, url):
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    LOG.info("Image downloaded successfully")
                    return await response.read()
                else:
                    exc = f"Image download failed with status code {response.status}"
                    LOG.exception(exc)
                    raise Exception(exc)

    async def upload_file_to_ipfs(self, file):
        headers = {
            "Authorization": f"Bearer {self.ipfs_key}",
        }

        LOG.info("Uploading image to NFTStorage")

        async with ClientSession() as session:
            async with session.post(
                "https://api.nft.storage/upload",
                headers=headers,
                data=file
            ) as resp:
                if resp.status == 200:
                    LOG.info("Image uploaded successfully to IPFS")
                    json_response = await resp.json()
                    cid = json_response["value"]["cid"]
                    link = f"https://{cid}.ipfs.nftstorage.link"
                    LOG.info(f"Link to DALLE image is {link}")
                    return link
                else:
                    LOG.exception(await resp.text())
                    exc = f"File upload failed with status code {resp.status}"
                    LOG.exception(exc)
                    raise Exception(exc)
