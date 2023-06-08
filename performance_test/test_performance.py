import os
import time
from web3 import Web3, exceptions
from dotenv import load_dotenv
from threading import Thread
from utils.ipfs import IPFS
from utils.check_dependencies import getDependencies


load_dotenv()

with open("abi.json", "r") as file:
    abi = file.read()

with open("token_abi.json", "r") as file:
    token_abi = file.read()

w3: Web3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_ADDRESS")))
chain_id: int = 1337
contract = w3.eth.contract(address=os.getenv("CONTRACT_ADDRESS"), abi=abi)
token_contract = w3.eth.contract(
    address=os.getenv("TOKEN_CONTRACT_ADDRESS"), abi=token_abi
)
ipfs_auth_token: str = os.getenv("IPFS_AUTH_TOKEN")
execution_times = {}
threads = []
ipfs = IPFS(contract, ipfs_auth_token)

public_keys = []
private_keys = []


def parse_ganache_file():
    with open("ganache.txt", "r") as file:
        lines = file.readlines()
    pk = False
    for line in lines:
        if line.strip() == "Private Keys":
            pk = True
        if line[0] == "(":
            if pk == False:
                tmp = line.split()
                public_keys.append(tmp[1])
            else:
                tmp = line.split()
                private_keys.append(tmp[1])
    keys = dict(zip(public_keys, private_keys))
    return keys


def thread_function(id: int, addr: str, private_key: str):
    nonce: int = w3.eth.getTransactionCount(addr)
    nonce = register_developer(id, addr, private_key, nonce)
    if id == 0:
        nonce = create_groups(id, addr, private_key, nonce)
        nonce = create_projects_with_names(
            id, addr, private_key, nonce, ["print_hi", "print_hi_n_times"]
        )
        nonce = load_libraries(id, addr, private_key, nonce)
    else:
        threads[0].join()
    start_time = time.time()
    for _ in range(2):
        nonce = check_dependencies_reliability(id, addr, private_key, nonce)
    end_time = time.time()
    execution_times[id] = end_time - start_time


def register_developer(id: int, addr: str, private_key: str, nonce: int):
    n_tokens = 100000
    print(f"Buying {n_tokens} SCT by thread {id}...")
    createTransaction(
        contract.functions.buyTokens,
        value=n_tokens,
        nonce=nonce,
        wait=True,
        addr=addr,
        private_key=private_key,
    )
    nonce += 1
    approveTokenFee(3000, nonce=nonce, addr=addr, private_key=private_key)
    email = f"test{id}@test.it"
    nonce += 1
    createTransaction(
        contract.functions.addDeveloper,
        email,
        nonce=nonce,
        wait=True,
        addr=addr,
        private_key=private_key,
    )
    print(f"Registering a developer with email {email}")
    return nonce


def create_groups(id: int, addr: str, private_key: str, nonce: int):
    try:
        n_groups = 1
        start_time = time.time()
        print(f"Creating {n_groups} groups by thread {id}...")
        for i in range(n_groups):
            nonce += 1
            approveTokenFee(2000, nonce=nonce, addr=addr, private_key=private_key)
            nonce += 1
            createTransaction(
                contract.functions.createGroup,
                f"group{id}_{i}",
                nonce=nonce,
                wait=True,
                addr=addr,
                private_key=private_key,
            )

        end_time = time.time()
        execution_times[id] = end_time - start_time
        print(f"Thread {id} time (group creation): {end_time - start_time}")
        return nonce
    except exceptions.SolidityError as error:
        print(f"Something went wrong in thread {id}")
        print(error)


def create_projects(id: int, addr: str, private_key: str, nonce: int):
    try:
        n_projects = 2
        start_time = time.time()
        print(f"Creating {n_projects} projects by thread {id}...")
        for i in range(n_projects):
            nonce += 1
            approveTokenFee(2000, nonce=nonce, addr=addr, private_key=private_key)
            nonce += 1
            createTransaction(
                contract.functions.createProject,
                f"group{id}_0",
                f"project{id}_{i}",
                nonce=nonce,
                wait=True,
                addr=addr,
                private_key=private_key,
            )

        end_time = time.time()
        execution_times[id] = end_time - start_time
        print(f"Thread {id} time (project creation): {end_time - start_time}")
        return nonce
    except exceptions.SolidityError as error:
        print(f"Something went wrong in thread {id}")
        print(error)


def create_projects_with_names(
    id: int, addr: str, private_key: str, nonce: int, names: list
):
    try:
        start_time = time.time()
        print(f"Creating {len(names)} projects by thread {id}...")
        for i in names:
            nonce += 1
            approveTokenFee(2000, nonce=nonce, addr=addr, private_key=private_key)
            nonce += 1
            createTransaction(
                contract.functions.createProject,
                f"group{id}_0",
                i,
                nonce=nonce,
                wait=True,
                addr=addr,
                private_key=private_key,
            )

        end_time = time.time()
        execution_times[id] = end_time - start_time
        print(f"Thread {id} time (project creation): {end_time - start_time}")
        return nonce
    except exceptions.SolidityError as error:
        print(f"Something went wrong in thread {id}")
        print(error)


def load_libraries(id: int, addr: str, private_key: str, nonce: int):
    try:
        with open("print_hi.js", "r") as f:
            file = f.read()
        print(f"Adding a version in the project print_hi...")
        CID1: str = ipfs.uploadFile(file)["cid"]
        nonce += 1
        approveTokenFee(1000, nonce=nonce, addr=addr, private_key=private_key)
        nonce += 1
        createTransaction(
            contract.functions.addLibrary,
            f"print_hi",
            CID1,
            "1.0.0",
            [""],
            nonce=nonce,
            wait=True,
            addr=addr,
            private_key=private_key,
        )

        with open("print_hi_n_times.js", "r") as f:
            file = f.read()
        print(f"Adding a version in the project print_hi_n_times...")

        CID2: str = ipfs.uploadFile(file)["cid"]
        nonce += 1
        approveTokenFee(1000, nonce=nonce, addr=addr, private_key=private_key)
        nonce += 1
        createTransaction(
            contract.functions.addLibrary,
            f"print_hi_n_times",
            CID2,
            "1.0.0",
            [CID1],
            nonce=nonce,
            wait=True,
            addr=addr,
            private_key=private_key,
        )
        return nonce
    except exceptions.SolidityError as error:
        print(f"Something went wrong in thread {id}")
        print(error)


def check_dependencies_reliability(id: int, addr: str, private_key: str, nonce: int):
    CID = contract.functions.getProjectLastVersion("print_hi_n_times").call()
    nonce += 1
    receipt = createTransaction(
        contract.functions.getLibraryInformationWithLevel,
        CID,
        nonce=nonce,
        wait=True,
        addr=addr,
        private_key=private_key,
    )
    info = contract.events.LibraryInfo().processReceipt(receipt)[0]["args"]
    print(
        f"{info.project}\nLast version: {info.version}\nReliability: {info.reliability}\nReliability level: {info.level}"
    )
    dependencies = getDependencies("print_hi_n_times")
    for key in dependencies:
        if dependencies[key][0] == "^" or dependencies[key][0] == "~":
            dependencies[key] = dependencies[key][1:]
        CIDs = contract.functions.getProjectVersions(key).call()
        for CID in CIDs:
            nonce += 1
            receipt = createTransaction(
                contract.functions.getLibraryInformationWithLevel,
                CID,
                nonce=nonce,
                wait=True,
                addr=addr,
                private_key=private_key,
            )
            info = contract.events.LibraryInfo().processReceipt(receipt)[0]["args"]
            print(
                f"{info.project}\nLast version: {info.version}\nReliability: {info.reliability}\nReliability level: {info.level}"
            )
    return nonce


def createTransaction(
    fun,
    *parameters,
    value=0,
    nonce: int,
    addr: str,
    private_key: str,
    wait: bool = False,
):
    transaction = fun(*parameters).buildTransaction(
        {
            "chainId": chain_id,
            "from": addr,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce,
            "value": value,
        }
    )
    signed_transaction = w3.eth.account.sign_transaction(
        transaction, private_key=private_key
    )
    transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    if wait:
        return w3.eth.wait_for_transaction_receipt(transaction_hash)


def approveTokenFee(fee: int, nonce: int, addr: str, private_key: str):
    createTransaction(
        token_contract.functions.approve,
        contract.address,
        fee,
        nonce=nonce,
        addr=addr,
        private_key=private_key,
        wait=True,
    )


if __name__ == "__main__":
    keys: dict = parse_ganache_file()
    i: int = 0
    for addr in keys:
        t = Thread(target=thread_function, args=(i, addr, keys[addr]))
        i += 1
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    print(
        f"Execution time mean: {sum(execution_times.values())/len(execution_times.keys())}"
    )
