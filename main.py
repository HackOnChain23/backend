from PIL import Image
import json
import requests as r
import io

from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
from loguru import logger as LOG
from web3 import Web3

from image_modifier import generate_composite_image_background_position
from nft_storage_client import NFTStorageClient
from dalle import return_image
from get_json import balanceOf_call
from config import CONTRACT_ADDRESS


app = FastAPI()
client = NFTStorageClient()

with open("abi.json", "r") as file:
    contract_abi = json.load(file)["abi"]

w3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/mantle_testnet"))

if w3.is_connected():
    LOG.info("Connection Successful with Mantle testnet")
else:
    LOG.exception("Connection Failed with Mantle testnet")


origins: list[str] = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptInput(BaseModel):
    dalle_input: str


class MetadataInput(BaseModel):
    name: Optional[str]
    description: Optional[str]
    image: str
    position: int
    token_id: Optional[int]


@app.get("/healthcheck")
def read_root():
    """Just healthcheck"""
    return {"status": "ok"}


@app.post("/image")
def create_picture(first_art: UploadFile = File(...)):
    """Takes image file, returns url to IPFS Storage"""

    LOG.info(f"New NFT was initiated")

    response = client.upload_file(first_art.file)

    cid = response["value"]["cid"]
    ipfs_url = NFTStorageClient.generate_nft_storage_url(cid=cid)

    LOG.info(f"IPFS NTF url: {ipfs_url}")

    return {"url": ipfs_url}


@app.post("/metadata")
def add_metadata(metadata_input: MetadataInput):
    LOG.info("Metadata creation")

    if metadata_input.name:
        LOG.info("Minting NFT")
        template_image_path: str = "images/template.png"
        template_image = Image.open(template_image_path)

        try:
            response = r.get(f"https://{metadata_input.image}", stream=True)
            response.raise_for_status()
            overlay_image = Image.open(response.raw)
        except (r.exceptions.RequestException, IOError):
            raise HTTPException(
                status_code=400, detail="Failed to load the overlay image from the URL."
            )

        composite_image = generate_composite_image_background_position(
            template_image,
            overlay_image,
            metadata_input.position,
        )
        image_bytes = io.BytesIO()
        composite_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        template_image.close()
        overlay_image.close()

        response = client.upload_file(image_bytes)
        cid = response["value"]["cid"]
        ipfs_url = NFTStorageClient.generate_nft_storage_url(cid=cid)

        metadata, data = client.create_metadata_on_ipfs(
            metadata=metadata_input, whole_nft=ipfs_url
        )
        cid = metadata["value"]["cid"]
        ipfs_url = NFTStorageClient.generate_nft_storage_url(cid=cid)
        LOG.info(f"IPFS NTF url: {ipfs_url}")
        return f"https://{ipfs_url}"
    else:
        LOG.info("Updating NFT data")
        contract_address: str = CONTRACT_ADDRESS
        try:
            contract = w3.eth.contract(address=contract_address, abi=contract_abi)
            ipfs_url = contract.functions.tokenURI(metadata_input.token_id).call()
            ipfs_url_json = r.get(ipfs_url).json()
        except Exception:
            LOG.exception("Problem with calling tokenURI function")
            raise HTTPException(
                status_code=500, detail="Failed to connect with contract."
            )

        try:
            response = r.get(f"https://{metadata_input.image}", stream=True)
            response.raise_for_status()
            new_img = Image.open(response.raw)
        except (r.exceptions.RequestException, IOError):
            raise HTTPException(
                status_code=400,
                detail="Failed to load the overlay image from the URL.",
            )

        old_whole_img = ipfs_url_json["image"]
        try:
            response = r.get(old_whole_img, stream=True)
            response.raise_for_status()
            old_whole_img = Image.open(response.raw)
        except (r.exceptions.RequestException, IOError):
            raise HTTPException(
                status_code=400,
                detail="Failed to load the overlay image from the URL.",
            )

        composite_image = generate_composite_image_background_position(
            old_whole_img,
            new_img,
            metadata_input.position,
        )
        image_bytes = io.BytesIO()
        composite_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        new_img.close()
        old_whole_img.close()

        response = client.upload_file(image_bytes)
        cid = response["value"]["cid"]
        whole_nft = NFTStorageClient.generate_nft_storage_url(cid=cid)

        metadata, data = client.update_metadata_on_ipfs(
            old_metadata=ipfs_url_json,
            position=metadata_input.position,
            whole_nft=whole_nft,
            new_image_url=metadata_input.image,
        )
        cid = metadata["value"]["cid"]
        ipfs_url = NFTStorageClient.generate_nft_storage_url(cid=cid)
        LOG.info(f"IPFS NTF url: {ipfs_url}")
        return f"https://{ipfs_url}"


@app.post("/ai-prompt")
def ai_prompt(prompt: PromptInput):
    return return_image(prompt.dalle_input)


@app.get("/token-ids")
def get_tokens(wallet: str):
    return balanceOf_call(wallet)


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
