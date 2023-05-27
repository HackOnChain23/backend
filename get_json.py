import json
import requests
import os

from web3 import Web3

with open('contract.json', 'r') as file:
    contract_abi = json.load(file)["abi"]

w3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/mantle_testnet"))

#if w3.is_connected():
#    print("-" * 50)
#    print("Connection Successful")
#    print("-" * 50)
#else:
#    print("Connection Failed")
#

contract_address: str = "0x5DDdBf0C22d24D0aB4A042afd7bA7e7a2e63e835"

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
name = contract.functions.name().call()

def balanceOf_call(wallet:str):
    tokenOOBI_list = []
    tokenURI_list = [] 
    lista_jsonow = []
    balance_amount = contract.functions.balanceOf(wallet).call()
    tokenURI_dict = {
            'id': str,
            'name': str,
            'description':str,
            'image': str
            }

    for i in range(0, balance_amount):
        tokenOOBI_list.append(contract.functions.tokenOfOwnerByIndex(wallet, i))
       
    for j in range(len(tokenOOBI_list)):
        tokenURI_list.append(contract.functions.tokenURI(j).call())
    
    for k in range(len(tokenURI_list)):
        r = requests.get(tokenURI_list[k])
        a_z_blokczejnu = r.json()
        a_z_blokczejnu['id'] = tokenOOBI_list[k].call()
        lista_jsonow.append(a_z_blokczejnu)

    return lista_jsonow
       

print(balanceOf_call('0x1d81532a666bb93a610d62b62cc264fb9Bc704Ed'))
