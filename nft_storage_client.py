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

    def create_metadata_on_ipfs(self, metadata, whole_nft):
        data = {
            "name": metadata.name,
            "description": metadata.description,
            "image": f"https://{whole_nft}",
            "parts": ["" for _ in range(6)],
        }
        data["parts"][metadata.position - 1] = f"https://{metadata.image}"

        data_io = io.StringIO()
        json.dump(data, data_io)
        data_io.seek(0)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = r.post("https://api.nft.storage/upload", headers=headers, data=data_io)

        if resp.status_code == 200:
            LOG.info("Metadata uploaded successfully")
            return resp.json(), data
        else:
            LOG.exception(
                f"Metadata storage failed with status code {resp.status_code}"
            )
            raise Exception(
                f"Metadata storage failed with status code {resp.status_code}"
            )

    def update_metadata_on_ipfs(self, old_metadata, position, whole_nft, new_image_url):
        LOG.info(f"Position to update: {position}")
        output = {
            "name": old_metadata["name"],
            "description": old_metadata["description"],
            "image": f"https://{whole_nft}",
            "parts": list(old_metadata["parts"]),
        }
        index_to_update: int = position - 1
        LOG.info(f"Updating index {index_to_update} in parts")
        output["parts"][index_to_update] = f"https://{new_image_url}"

        data_io = io.StringIO()
        json.dump(output, data_io)
        data_io.seek(0)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = r.post("https://api.nft.storage/upload", headers=headers, data=data_io)

        if resp.status_code == 200:
            LOG.info("Metadata uploaded successfully")
            LOG.info(f"Metadata: {output}")
            return resp.json(), output
        else:
            LOG.exception(
                f"Metadata storage failed with status code {resp.status_code}"
            )
            raise Exception(
                f"Metadata storage failed with status code {resp.status_code}"
            )

    def generate_nft_storage_url(cid: str):
        return cid + ".ipfs.nftstorage.link"
