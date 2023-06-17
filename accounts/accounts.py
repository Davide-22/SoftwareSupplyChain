import os
import random
import sys
import requests
from eth_account import Account
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


w3: Web3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_ADDRESS")))
chain_id = int(os.getenv("CHAIN_ID"))


def create_accounts():
    addresses = []
    private_keys = []
    for i in range(n_accounts):
        account = Account.create(
            str(i)
            + "asdasqui798hu2 òèì982adiashoi y3uijnm  à+òè+òò§°ç§ç§§°à acajlposbc8afas9fh fadsfaf8rnòlnn qgpvbbc29èà"
            + str(random.randint(0, 1000000000000000))
        )
        addresses.append(account.address)
        private_keys.append(account.privateKey.hex())
    return addresses, private_keys


if __name__ == "__main__":
    if len(sys.argv) == 3 and "--create" in sys.argv:
        n_accounts = int(sys.argv[1])
        print(f"Creating {n_accounts} accounts...")
        addresses, private_keys = create_accounts()
        with open("accounts/accounts.txt", "w") as f:
            f.write("Available Accounts\n==================\n")
            for i in range(len(addresses)):
                f.write(f"({i}) {addresses[i]}\n")
            f.write("\nPrivate Keys\n==================\n")
            for i in range(len(private_keys)):
                f.write(f"({i}) {private_keys[i]}\n")
        print(f"{n_accounts} accounts created")
    elif len(sys.argv) == 2 and "--balances" in sys.argv:
        with open("accounts/accounts.txt", "r") as f:
            for line in f.readlines():
                if line[0] == "(":
                    account = line.strip().split()[1]
                    print(f"{account}: {w3.eth.getBalance(account)}")
                if line == "Private Keys\n":
                    break

    else:
        print("Invalid command")


def send_ether(to: str, wei_to_send: int, sender: str, private_key: str):
    nonce = w3.eth.getTransactionCount(sender)
    tx = {
        "nonce": nonce,
        "to": to,
        "value": wei_to_send,
        "gasPrice": w3.eth.gas_price,
    }
    signed_transaction = w3.eth.account.sign_transaction(tx, private_key)

    transaction_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)

    return w3.eth.wait_for_transaction_receipt(transaction_hash)
