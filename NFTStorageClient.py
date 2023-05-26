import requests as r
import pprint

from config import NFT_STORAGE_API_KEY

pp = pprint.PrettyPrinter(indent=4)


class NFTStorageClient:
    def __init__(self):
        self.api_key = NFT_STORAGE_API_KEY

    def upload_file(self, file_path):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        with open(file_path, "rb") as file:
            resp = r.post(
                "https://api.nft.storage/upload",
                headers=headers,
                data=file
            )

        pp.pprint(f"Status code: {resp.status_code}")
        pp.pprint(resp.json())

        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"File upload failed with status code {resp.status_code}")

    def get_file_metadata(self, cid):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = r.get(
            f"https://api.nft.storage/{cid}",
            headers=headers
        )

        pp.pprint(f"Status code: {resp.status_code}")
        pp.pprint(resp.json())

        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Failed to retrieve file metadata with status code {resp.status_code}")


client = NFTStorageClient()

image_path = "images/image1.png"
response = client.upload_file(image_path)

cid = response["value"]["cid"]

metadata = client.get_file_metadata(cid)
pp.pprint(metadata)

# image_url = metadata["data"]["image"]["url"]
# print(f"Image URL: {image_url}")
