import io
import json

import requests as r

from loguru import logger as LOG

from config import NFT_STORAGE_API_KEY


class NFTStorageClient:
    def __init__(self):
        self.api_key = NFT_STORAGE_API_KEY

    def upload_file_on_ipfs(self, file):
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
            cid = resp.json()["value"]["cid"]
            link = f"https://{cid}.ipfs.nftstorage.link"
            LOG.info(f"Link to image is {link}")
            return link
        else:
            err = f"File upload failed with status code {resp.status_code}"
            LOG.exception(err)
            raise Exception(err)

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

    def upload_json_on_ipfs(self, mint_info, nft):
        data = {
            "name": mint_info.name,
            "description": mint_info.description,
            "image": nft,
            "parts": ["" for _ in range(6)],
        }
        data["parts"][mint_info.position - 1] = mint_info.image

        data_io = io.StringIO()
        json.dump(data, data_io)
        data_io.seek(0)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = r.post("https://api.nft.storage/upload", headers=headers, data=data_io)

        if resp.status_code == 200:
            LOG.info("Mint JSON data uploaded successfully")
            cid = resp.json()["value"]["cid"]
            ipfs_url = f"https://{cid}.ipfs.nftstorage.link"
            LOG.info(f"Link to JSON is {ipfs_url}")
            return ipfs_url
        else:
            err = f"Saving Mint data on storage failed with status code {resp.status_code}"
            LOG.exception(err)
            raise Exception(err)

    def update_json_on_ipfs(self, nft_data, new_nft_grid, new_nft_part_url, position):
        LOG.info(f"New NFT will be added to the position: {position}")
        output = {
            "name": nft_data["name"],
            "description": nft_data["description"],
            "image": new_nft_grid,
            "parts": nft_data["parts"],
        }
        index_to_update: int = position - 1
        LOG.info(f"In parts list updating index: {index_to_update}")
        output["parts"][index_to_update] = new_nft_part_url

        data_io = io.StringIO()
        json.dump(output, data_io)
        data_io.seek(0)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = r.post("https://api.nft.storage/upload", headers=headers, data=data_io)

        if resp.status_code == 200:
            LOG.info("NFT JSON uploaded successfully")
            cid = resp.json()["value"]["cid"]
            ipfs_url = f"https://{cid}.ipfs.nftstorage.link"
            LOG.info(f"Link to updated JSON is: {ipfs_url}")
            return ipfs_url
        else:
            err = f"Updating JSON data on storage failed with status code {resp.status_code}"
            LOG.exception(err)
            raise Exception(err)
