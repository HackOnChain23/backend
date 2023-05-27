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

contract_address: str = "0xC700aA5AD1f437e42Dc690CA5711ec6bc47B3Fc3"

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
# name = contract.functions.name().call({'from': "0xD6D610866A888Ce99c0778EE518D7628c1A9a1e4"})
name = contract.functions.name().call()

def balanceOf_call(wallet:str):
    return contract.functions.balanceOf(wallet)

def tokenOfOwnerByIndex_call(balanceof:int):


balanceof = balanceOf_call('0x1d81532a666bb93a610d62b62cc264fb9Bc704Ed').call()
print(balanceof)
print('dupa')
