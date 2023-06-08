import json
import os
from solcx import install_solc, compile_source
from web3 import Web3
from dotenv import load_dotenv, find_dotenv, set_key
from os.path import exists

if not exists(".env"):
    dotenv_file = ".env"
    open(dotenv_file, "w")
    private_key =  input("Insert the private key: ")
    set_key(dotenv_file, "PRIVATE_KEY", private_key)

    address = input("Insert the wallet address: ")
    set_key(dotenv_file, "ADDRESS", address)

    blockchain_address = input("Insert the blockchain address: ")
    set_key(dotenv_file, "BLOCKCHAIN_ADDRESS", blockchain_address)

    ipfs_token = input("Insert the IPFS auth token: ")
    set_key(dotenv_file, "IPFS_AUTH_TOKEN", ipfs_token)
else:
    dotenv_file = find_dotenv()  
    
load_dotenv()

with open("./ERC20/SupplyChainToken.sol", "r") as file:
    sol_file = file.read()

install_solc("0.8.0")

w3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_ADDRESS")))
chain_id = 1337
addr = os.getenv("ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
initial_tokens = 100000000000
max_reliability = 20
reliability_cost = 50


def deploy_contract(name: str, path: str, *params):
    with open(f".{path}/{name}.sol", "r") as file:
        sol_file = file.read()

    compiled_sol = compile_source(
        sol_file,
        output_values=["abi", "bin"],
        solc_version="0.8.0",
        optimize=True,
    )
    bytecode = compiled_sol[f"<stdin>:{name}"]["bin"]
    abi = compiled_sol[f"<stdin>:{name}"]["abi"]
    print(len(bytecode) / 2)

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.getTransactionCount(addr)

    transaction = contract.constructor(*params).buildTransaction(
        {
            "chainId": chain_id,
            "from": addr,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce,
        }
    )

    singned_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(singned_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return abi, tx_receipt.contractAddress


"""Deploy the SupplyChainToken contract"""
token_abi, token_address = deploy_contract("SupplyChainToken", "/ERC20", initial_tokens)
print(f"SupplyChainToken contract address: {token_address}")
set_key(dotenv_file, "TOKEN_CONTRACT_ADDRESS", token_address)

with open("token_abi.json", "w") as file:
    json.dump(token_abi, file)

"""Deploy the SoftwareSupplyChain contract"""
abi, address = deploy_contract("SoftwareSupplyChain", "", token_address, max_reliability, reliability_cost)
print(f"SoftwareSupplyChain contract address: {address}")
set_key(dotenv_file, "CONTRACT_ADDRESS", address)

with open("abi.json", "w") as file:
    json.dump(abi, file)

"""Transfer tokens from the deployer to the SoftwareSupplyChain contract"""
nonce: int = w3.eth.getTransactionCount(addr)
contract = w3.eth.contract(address=token_address, abi=token_abi)
transaction = contract.functions.transfer(address, initial_tokens).buildTransaction(
    {
        "chainId": chain_id,
        "from": addr,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce
    }
)
signed_transaction = w3.eth.account.sign_transaction(
    transaction, private_key=private_key
)
transaction_hash = w3.eth.send_raw_transaction(
    signed_transaction.rawTransaction
)
tx_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)

