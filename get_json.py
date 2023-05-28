import json
import requests

from web3 import Web3
from config import CONTRACT_ADDRESS

with open("abi.json", "r") as file:
    contract_abi = json.load(file)["abi"]

w3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/mantle_testnet"))

contract_address: str = CONTRACT_ADDRESS

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
name = contract.functions.name().call()


def balanceOf_call(wallet: str):
    tokenOOBI_list = []
    tokenURI_list = []
    lista_jsonow = []
    balance_amount = contract.functions.balanceOf(wallet).call()

    for i in range(0, balance_amount):
        tokenOOBI_list.append(contract.functions.tokenOfOwnerByIndex(wallet, i))
    for j in range(len(tokenOOBI_list)):
        tokenURI_list.append(contract.functions.tokenURI(j).call())

    for k in range(len(tokenURI_list)):
        r = requests.get(tokenURI_list[k])
        a_z_blokczejnu = r.json()
        a_z_blokczejnu["id"] = tokenOOBI_list[k].call()
        lista_jsonow.append(a_z_blokczejnu)

    return lista_jsonow


# print(balanceOf_call("0x8caEa39280b90F74BB2251cbD46b85f7A500dd89"))
