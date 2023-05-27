import json

from web3 import Web3

with open('contract.json', 'r') as file:
    contract_abi = json.load(file)["abi"]

w3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/mantle_testnet"))

if w3.is_connected():
    print("-" * 50)
    print("Connection Successful")
    print("-" * 50)
else:
    print("Connection Failed")

contract_address: str = "0x5DDdBf0C22d24D0aB4A042afd7bA7e7a2e63e835"

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
name = contract.functions.name().call()

def balanceOf_call(wallet:str):
    tokenOOBI_list = []
    balance_amount = contract.functions.balanceOf(wallet).call()
    print(balance_amount) 
    for i in range(0, balance_amount):
        tokenOOBI_list.append(contract.functions.tokenOfOwnerByIndex(wallet, balance_amount))

    tokenURI_list = []    
    for j in range(len(tokenOOBI_list)):
        tokenURI_list.append(contract.functions.tokenURI(j).call())

    return tokenURI_list

balanceof = balanceOf_call('0x1d81532a666bb93a610d62b62cc264fb9Bc704Ed')

print(balanceof)
print('dupa')
