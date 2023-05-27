import io
import json

import requests as r

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

    def upload_json(self, metadata):
        data = {
            "name": metadata.name,
            "description": metadata.description,
            "image": metadata.image,  # TODO: add combined images
            "nftParts": [
                metadata.image,
            ]
        }

        data_io = io.StringIO()
        json.dump(data, data_io)
        data_io.seek(0)

        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweGQzZTQ1ZTkyZmZiMzQ1RDdmZTQ2MzhkZDIyODZBM2U0ODNBODE2NjMiLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTY4NDc4MzE3OTcyOSwibmFtZSI6ImFydF9tZXJnZSJ9.67_OKDpOJ_qk_vskD_qyJJIr3xNowQzueCFWRg2BKBY',
        }

        resp = r.post("https://api.nft.storage/upload", headers=headers, data=data_io)

        if resp.status_code == 200:
            LOG.info("Metadata uploaded successfully")
            return resp.json()
        else:
            LOG.exception(f"Metadata storage failed with status code {resp.status_code}")
            raise Exception(f"Metadata storage failed with status code {resp.status_code}")

    def generate_nft_storage_url(cid: str):
        return cid + ".ipfs.nftstorage.link"
