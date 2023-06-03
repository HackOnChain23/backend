import requests as r
import io
import asyncio

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
from loguru import logger as LOG
from PIL import Image

import blockchain
from models import DalleInput, NftUpdate, MintInput
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
    """Mint a new NFT from an image URL and returns the IPFS URL of the minting data."""
    LOG.info("Creating data needed for NFT minting")
    LOG.info(f"Mint NFT: {mint_input}")

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
    """Add a new part of NFT and returns the IPFS URL of the updated data."""
    LOG.info("Updating NFT data")
    LOG.info(f"Update NFT: {nft_update}")


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
    LOG.info(f"Tokens for wallet: {wallet}")
    return blockchain.fetch_owned_tokens_info(wallet)


# import uvicorn
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
