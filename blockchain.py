import json
import requests as r

from typing import List, Dict

from fastapi import HTTPException
from loguru import logger as LOG
from web3 import Web3

from config import SMART_CONTRACT_ADDRESS


with open("abi.json", "r") as file:
    contract_abi = json.load(file)["abi"]

w3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/mantle_testnet"))

if w3.is_connected():
    LOG.info("Connection Successful with Mantle testnet")
else:
    LOG.exception("Connection Failed with Mantle testnet")

contract = w3.eth.contract(address=SMART_CONTRACT_ADDRESS, abi=contract_abi)
name = contract.functions.name().call()


def fetch_owned_tokens_info(wallet: str) -> List[Dict]:
    """
    Fetch token metadata associated with a specific wallet.

    Args:
        wallet: Wallet address as a string.

    Returns:
        List of JSON data representing token metadata.
    """
    metadata_list = []
    balance_amount = contract.functions.balanceOf(wallet).call()

    # Collect token metadata associated with the wallet
    for i in range(0, balance_amount):
        try:
            # Get token ID
            token_id = contract.functions.tokenOfOwnerByIndex(wallet, i).call()

            # Fetch token URI
            token_uri = contract.functions.tokenURI(token_id).call()

            # Retrieve metadata from URI
            response = r.get(token_uri)
            response.raise_for_status()
            metadata = response.json()
            metadata["id"] = token_id
            metadata_list.append(metadata)

        except Exception as e:
            LOG.exception(
                f"Failed to fetch or parse JSON for token id {token_id}. Error: {e}"
            )

    return metadata_list


def get_ipfs_url_by_given_token_id(token_id: int):
    try:
        ipfs_url = contract.functions.tokenURI(token_id).call()
        ipfs_json = r.get(ipfs_url).json()
    except Exception:
        LOG.exception("Problem with calling tokenURI function")
        raise HTTPException(status_code=500, detail="Failed to connect with contract.")
    return ipfs_json


# res = fetch_owned_tokens_info("0xD6D610866A888Ce99c0778EE518D7628c1A9a1e4")
# print(res)
