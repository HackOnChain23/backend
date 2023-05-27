import requests as r
import pprint

from loguru import logger as LOG

from config import NFT_STORAGE_API_KEY


class NFTStorageClient:
    def __init__(self):
        self.api_key = NFT_STORAGE_API_KEY

    def upload_file(self, file):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        LOG.info("Uploading image to NFTStorage")

        resp = r.post(
            "https://api.nft.storage/upload",
            headers=headers,
            data=file,
        )

        if resp.status_code == 200:
            LOG.info("Image uploaded successfully")
            return resp.json()
        else:
            LOG.exception(f"File upload failed with status code {resp.status_code}")
            raise Exception(f"File upload failed with status code {resp.status_code}")

    def get_file_metadata(self, cid):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = r.get(
            f"https://api.nft.storage/{cid}",
            headers=headers,
        )

        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(
                f"Failed to retrieve file metadata with status code {resp.status_code}"
            )

    def generate_nft_storage_url(cid: str):
        return cid + ".ipfs.nftstorage.link"
