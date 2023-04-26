import json
import os
from solcx import install_solc, compile_source
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./ERC20/SupplyChainToken.sol", "r") as file:
    sol_file = file.read()

install_solc("0.8.0")

w3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_ADDRESS")))
chain_id = 1337
addr = os.getenv("ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
initial_tokens = 1000000000


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
abi, address = deploy_contract("SupplyChainToken", "/ERC20", initial_tokens)

"""Deploy the SoftwareSupplyChain contract"""
abi, address = deploy_contract("SoftwareSupplyChain", "", address)

with open("abi.json", "w") as file:
    json.dump(abi, file)
print(address)
