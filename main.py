from PIL import Image
import io

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from loguru import logger as LOG

from image_modifier import generate_composite_image_background_position
from nft_storage_client import NFTStorageClient
from invitations import generate_invitation_code

app = FastAPI()

client = NFTStorageClient()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}


@app.post("/image/")
def create_picture(wallet_address: str, first_art: UploadFile = File(...)):
    LOG.info(f"New art was initiated by the wallet: {wallet_address}")

    template_image_path: str = "images/template.png"
    template_image = Image.open(template_image_path)

    image = Image.open(first_art.file)

    composite_image = generate_composite_image_background_position(
        template_image, image, 1
    )

    image_bytes = io.BytesIO()
    composite_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.upload_file(image_bytes)

    cid = response["value"]["cid"]

    url = NFTStorageClient.generate_nft_storage_url(cid=cid)
    LOG.info(f"NTF url: {url}")

    # save to database (wallet_address, invitation_code, url)
    # do we need wallet address? or only invitation code is needed?

    return {"url": url}


@app.patch("/image/{position}")
def update_picture(position: int, file: UploadFile = File(...)):
    LOG.info(f"Updating position {position}")
    return {"filename": file.filename}


# @app.patch("/update-file/{position}")
# async def update_picture(position: int, file: UploadFile = File(...)):
#     return {"filename": file.filename}
