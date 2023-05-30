import requests as r
import io
import asyncio

from typing import Optional
import blockchain
from pydantic import BaseModel, validator
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
from loguru import logger as LOG
from PIL import Image

from image_modifier import generate_grid_with_initial_image_on_given_position
from nft_storage_client import NFTStorageClient
from dalle import Dalle

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = NFTStorageClient()


class DalleInput(BaseModel):
    prompt: str

    @validator("prompt")
    def check_length(cls, v):
        if len(v) > 20:
            raise ValueError("This input is too long. Enter less than 20 characters")
        return v


class MintInput(BaseModel):
    name: str
    description: str
    image: str
    position: int

    @validator("image")
    def image_url_must_be_valid(cls, v):
        if not v.startswith("https://"):
            raise ValueError("Image URL must start with: https://")
        if not v.endswith(".ipfs.nftstorage.link"):
            raise ValueError("Image URL must end with: .ipfs.nftstorage.link")
        return v


class NftUpdate(BaseModel):
    image: str
    position: int
    token_id: int

    @validator("image")
    def image_url_must_be_valid(cls, v):
        if not v.startswith("https://"):
            raise ValueError("Image URL must start with: https://")
        if not v.endswith(".ipfs.nftstorage.link"):
            raise ValueError("Image URL must end with: .ipfs.nftstorage.link")
        return v


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

    ipfs_url = client.upload_file_on_ipfs(first_art.file)

    LOG.info(f"IPFS NTF url: {ipfs_url}")

    return {"url": ipfs_url}


@app.post("/mint")
def mint_nft(mint_input: MintInput):
    LOG.info("Creating data needed for NFT minting")

    # Load the given image
    try:
        response = r.get(mint_input.image, stream=True)
        response.raise_for_status()
        initial_image = Image.open(response.raw)
    except (r.exceptions.RequestException, IOError):
        raise HTTPException(
            status_code=400, detail="Failed to load the initial_image from the URL."
        )

    # Prepare grid for NFT with initial image
    template_image_path: str = "images/template.png"
    template_image = Image.open(template_image_path)

    composite_image = generate_grid_with_initial_image_on_given_position(
        template_image,
        initial_image,
        mint_input.position,
    )
    image_bytes = io.BytesIO()
    composite_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    template_image.close()
    initial_image.close()

    # Upload NFT image on IPFS
    ipfs_url = client.upload_file_on_ipfs(image_bytes)

    # Upload Mint JSON data on IPFS
    json_ipfs_url = client.upload_json_on_ipfs(
        mint_info=mint_input,
        nft=ipfs_url,
    )

    return json_ipfs_url


@app.patch("/nft")
def add_part_of_nft(nft_update: NftUpdate):
    LOG.info("Updating NFT data")

    # Get NFT JSON data from IPFS by given token_id
    nft_data = blockchain.get_ipfs_url_by_given_token_id(token_id=nft_update.token_id)

    # Load new part of NFT
    try:
        response = r.get(nft_update.image, stream=True)
        response.raise_for_status()
        new_nft_part_image = Image.open(response.raw)
    except (r.exceptions.RequestException, IOError):
        raise HTTPException(
            status_code=400,
            detail="Failed to load new NFT image from the URL.",
        )

    # Load whole grid of NFTs
    whole_image_url = nft_data["image"]
    try:
        response = r.get(whole_image_url, stream=True)
        response.raise_for_status()
        whole_img = Image.open(response.raw)
    except (r.exceptions.RequestException, IOError):
        raise HTTPException(
            status_code=400,
            detail="Failed to load the whole NFT image from the URL.",
        )

    # Update old grid to with new NFT part
    new_nft_grid = generate_grid_with_initial_image_on_given_position(
        whole_img,
        new_nft_part_image,
        nft_update.position,
    )
    image_bytes = io.BytesIO()
    new_nft_grid.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    new_nft_part_image.close()
    whole_img.close()

    new_nft_grid_url = client.upload_file_on_ipfs(image_bytes)

    # Create new updated JSON NFTs data
    ipfs_url = client.update_json_on_ipfs(
        nft_data=nft_data,
        new_nft_grid=new_nft_grid_url,
        new_nft_part_url=nft_update.image,
        position=nft_update.position,
    )
    return ipfs_url


# @app.post("/metadata")
# def add_metadata(metadata_input: MetadataInput):
#     LOG.info("Metadata creation")
#
#     if metadata_input.name:
#         LOG.info("Minting NFT")
#         template_image_path: str = "images/template.png"
#         template_image = Image.open(template_image_path)
#
#         try:
#             response = r.get(f"https://{metadata_input.image}", stream=True)
#             response.raise_for_status()
#             overlay_image = Image.open(response.raw)
#         except (r.exceptions.RequestException, IOError):
#             raise HTTPException(
#                 status_code=400, detail="Failed to load the overlay image from the URL."
#             )
#
#         composite_image = generate_composite_image_background_position(
#             template_image,
#             overlay_image,
#             metadata_input.position,
#         )
#         image_bytes = io.BytesIO()
#         composite_image.save(image_bytes, format="PNG")
#         image_bytes.seek(0)
#
#         template_image.close()
#         overlay_image.close()
#
#         response = client.upload_file_on_ipfs(image_bytes)
#         cid = response["value"]["cid"]
#         ipfs_url = NFTStorageClient.generate_nft_storage_url(cid=cid)
#
#         metadata, data = client.create_metadata_on_ipfs(
#             metadata=metadata_input, whole_nft=ipfs_url
#         )
#         cid = metadata["value"]["cid"]
#         ipfs_url = NFTStorageClient.generate_nft_storage_url(cid=cid)
#         LOG.info(f"IPFS NTF url: {ipfs_url}")
#         return f"https://{ipfs_url}"
#     else:
#         LOG.info("Updating NFT data")
#         contract_address: str = SMART_CONTRACT_ADDRESS
#         try:
#             contract = w3.eth.contract(address=contract_address, abi=contract_abi)
#             ipfs_url = contract.functions.tokenURI(metadata_input.token_id).call()
#             ipfs_url_json = r.get(ipfs_url).json()
#         except Exception:
#             LOG.exception("Problem with calling tokenURI function")
#             raise HTTPException(
#                 status_code=500, detail="Failed to connect with contract."
#             )
#
#         try:
#             response = r.get(f"https://{metadata_input.image}", stream=True)
#             response.raise_for_status()
#             new_img = Image.open(response.raw)
#         except (r.exceptions.RequestException, IOError):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Failed to load the overlay image from the URL.",
#             )
#
#         old_whole_img = ipfs_url_json["image"]
#         try:
#             response = r.get(old_whole_img, stream=True)
#             response.raise_for_status()
#             old_whole_img = Image.open(response.raw)
#         except (r.exceptions.RequestException, IOError):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Failed to load the overlay image from the URL.",
#             )
#
#         composite_image = generate_composite_image_background_position(
#             old_whole_img,
#             new_img,
#             metadata_input.position,
#         )
#         image_bytes = io.BytesIO()
#         composite_image.save(image_bytes, format="PNG")
#         image_bytes.seek(0)
#
#         new_img.close()
#         old_whole_img.close()
#
#         response = client.upload_file_on_ipfs(image_bytes)
#         cid = response["value"]["cid"]
#         whole_nft = NFTStorageClient.generate_nft_storage_url(cid=cid)
#
#         metadata = client.update_metadata_on_ipfs(
#             old_metadata=ipfs_url_json,
#             position=metadata_input.position,
#             whole_nft=whole_nft,
#             new_image_url=metadata_input.image,
#         )
#         cid = metadata["value"]["cid"]
#         ipfs_url = NFTStorageClient.generate_nft_storage_url(cid=cid)
#         LOG.info(f"IPFS NTF url: {ipfs_url}")
#         return f"https://{ipfs_url}"


@app.post("/ai-generate")
async def ai_prompt(ai_input: DalleInput):
    """Generate 4 image ideas AI based on given prompt"""

    dalle = Dalle()
    delle_urls = await dalle.generate_image(ai_input.prompt, 4)

    tasks = []
    for url in delle_urls:
        downloaded_image = await dalle.download_image(url)
        tasks.append(dalle.upload_file_to_ipfs(downloaded_image))

    ipfs_url = await asyncio.gather(*tasks)

    return ipfs_url


@app.get("/token-ids")
def get_tokens(wallet: str):
    return blockchain.fetch_owned_tokens_info(wallet)
