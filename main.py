from PIL import Image
import io

from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from loguru import logger as LOG

from image_modifier import generate_composite_image_background_position
from nft_storage_client import NFTStorageClient

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


class MetadataInput(BaseModel):
    name: str
    description: str
    image: str
    position: int
    wallet_address: str
    token_id: str
    # nft_parts: List[str] = Field(..., alias='nftParts')


@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}


@app.post("/image")
def create_picture(first_art: UploadFile = File(...)):
    LOG.info(f"New NFT was initiated")

    response = client.upload_file(first_art.file)

    cid = response["value"]["cid"]
    url = NFTStorageClient.generate_nft_storage_url(cid=cid)

    LOG.info(f"NTF url: {url}")

    return {"url": url}

# @app.post("/image/{position}")
# def create_picture(position: int, first_art: UploadFile = File(...)):
#     LOG.info(f"New art was initiated with position: {position}")
#
#     # upload to ipfs
#     # dane od usera
#     # z danych tworzymy jsona nazwa URI
#     # upload jsona
#     # zrwotn na front
#
#     template_image_path: str = "images/template.png"
#     template_image = Image.open(template_image_path)
#
#     image = Image.open(first_art.file)
#
#     composite_image = generate_composite_image_background_position(
#         template_image, image, position,
#     )
#
#     image_bytes = io.BytesIO()
#     composite_image.save(image_bytes, format="PNG")
#     image_bytes.seek(0)
#
#     response = client.upload_file(image_bytes)
#
#     cid = response["value"]["cid"]
#
#     url = NFTStorageClient.generate_nft_storage_url(cid=cid)
#     LOG.info(f"NTF url: {url}")
#
#     # save to database (wallet_address, invitation_code, url)
#     # do we need wallet address? or only invitation code is needed?
#
#     return {"url": url}


@app.post("/metadata")
def add_metadata(metadata_input: MetadataInput):
    LOG.info(f"Metadata creation")

    metadata = client.upload_json(metadata=metadata_input)
    
    # metadata_input.token_id: str TUTAJ ODPYTUJE smartcontract?
    # token id jest po to do ktorego nfka mam dodac ta nowa czesc
    # adress walleta -> smartcontract
    # zwraca liste id dla danego usera
    # meczuje tokenId od palucha z lista token idkow od lecha

    #
    # smart contract functions
    # balanceOf(wallet_addres) -> ile lacznie mam nfki 3, 5
    # tokenOfOwnerByIndex(address owner, uint256 index) - 3,5 razy mysze wykonac to mi zraca tokenId

    LOG.info(f"Metadata: {metadata}")
    return metadata


@app.patch("/image/{position}")
def update_picture(position: int, file: UploadFile = File(...)):
    # get position from url

    # input wallet address
    # check wallet is owner of nft using smart contract
    # get url of image from given url
    # add image from

    LOG.info(f"Updating position {position}")
    return {"filename": file.filename}


# @app.patch("/update-file/{position}")
# async def update_picture(position: int, file: UploadFile = File(...)):
#     return {"filename": file.filename}
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
