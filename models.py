from pydantic import BaseModel, validator


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
