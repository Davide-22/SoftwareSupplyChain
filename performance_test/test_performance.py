import os, sys

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import random
from web3 import Web3
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
chain_id: int = int(os.getenv("CHAIN_ID"))
contract = w3.eth.contract(address=os.getenv("CONTRACT_ADDRESS"), abi=abi)
token_contract = w3.eth.contract(
    address=os.getenv("TOKEN_CONTRACT_ADDRESS"), abi=token_abi
)
ipfs_auth_token: str = os.getenv("IPFS_AUTH_TOKEN")
execution_times = {}
transactions_cost = {}
failed_threads = []
threads = []
transaction_type = ""
ipfs = IPFS(contract, ipfs_auth_token)

public_keys = []
private_keys = []


def parse_ganache_file(n: int = -1):
    with open("ganache.txt", "r") as file:
        lines = file.readlines()
    pk = False
    for line in lines:
        if line.strip() == "Private Keys":
            pk = True
        if line[0] == "(":
            if pk == False:
                if n == -1 or len(public_keys) < n:
                    tmp = line.split()
                    public_keys.append(tmp[1])
            else:
                if n == -1 or len(private_keys) < n:
                    tmp = line.split()
                    private_keys.append(tmp[1])
    keys = dict(zip(public_keys, private_keys))
    return keys


def thread_function_groups(id: int, addr: str, private_key: str):
    retry = 0
    while True:
        try:
            nonce: int = w3.eth.getTransactionCount(addr)
            break
        except requests.exceptions.HTTPError as e:
            if retry >= 20:
                print("retry = 20")
                return
            sleep = (2 ** retry + 
                 random.uniform(0, 2))
            print(f"[{id}] HTTP retry in {fun}. Attempt number {retry + 1}")
            time.sleep(sleep*0.1)
            retry += 1
    
    nonce = register_developer(id, addr, private_key, nonce)

    # Create groups test
    create_groups(id, addr, private_key, nonce, 10)


def thread_function_projects(id: int, addr: str, private_key: str):
    retry = 0
    while True:
        try:
            nonce: int = w3.eth.getTransactionCount(addr)
            break
        except requests.exceptions.HTTPError as e:
            if retry >= 20:
                print("retry = 20")
                return
            sleep = (2 ** retry + 
                 random.uniform(0, 2))
            print(f"[{id}] HTTP retry in getTransactionCount. Attempt number {retry + 1}")
            time.sleep(sleep*0.1)
            retry += 1
    nonce = register_developer(id, addr, private_key, nonce)

    # Create projects test
    nonce = create_groups(id, addr, private_key, nonce, 1)
    nonce = create_projects(id, addr, private_key, nonce, 10)


def thread_function_dependencies(id: int, addr: str, private_key: str):
    retry = 0
    while True:
        try:
            nonce: int = w3.eth.getTransactionCount(addr)
            break
        except requests.exceptions.HTTPError as e:
            if retry >= 20:
                print("retry = 20")
                return
            sleep = (2 ** retry + 
                 random.uniform(0, 2))
            print(f"[{id}] HTTP retry in getTransactionCount. Attempt number {retry + 1}")
            time.sleep(sleep*0.1)
            retry += 1
    nonce = register_developer(id, addr, private_key, nonce)

    # Check dependencies reliability test
    if id == 0:
        nonce = create_groups(id, addr, private_key, nonce, 1)
        nonce = create_projects_with_names(
            id, addr, private_key, nonce, ["print_hi", "print_hi_n_times"]
        )
        nonce = load_libraries(id, addr, private_key, nonce)
    else:
        threads[0].join()
    start_time = time.time()
    for _ in range(10):
        nonce = check_dependencies_reliability(id, addr, private_key, nonce)
    end_time = time.time()
    execution_times[id] = end_time - start_time


def register_developer(id: int, addr: str, private_key: str, nonce: int):
    try:
        n_tokens = 100000
        print(f"Buying {n_tokens} SCT by thread {id}...")
        createTransaction(
            contract.functions.buyTokens,
            value=n_tokens,
            nonce=nonce,
            wait=True,
            addr=addr,
            private_key=private_key,
            key="buy_tokens",
            id=id,
        )
        nonce += 1
        approveTokenFee(3000, nonce=nonce, addr=addr, private_key=private_key, id=id)
        email = f"test{id}@test.it"
        nonce += 1
        createTransaction(
            contract.functions.addDeveloper,
            email,
            nonce=nonce,
            wait=True,
            addr=addr,
            private_key=private_key,
            key="add_developer",
            id=id,
        )

        print(f"Registering a developer with email {email}")
        return nonce
    except Exception as error:
        handle_error(id=id, error=error)


def create_groups(id: int, addr: str, private_key: str, nonce: int, n_groups: int):
    try:
        start_time = time.time()
        print(f"Creating {n_groups} groups by thread {id}...")
        for i in range(n_groups):
            nonce += 1
            approveTokenFee(
                2000, nonce=nonce, addr=addr, private_key=private_key, id=id
            )
            nonce += 1
            createTransaction(
                contract.functions.createGroup,
                f"group{id}_{i}",
                nonce=nonce,
                wait=True,
                addr=addr,
                private_key=private_key,
                key="create_group",
                id=id,
            )

        end_time = time.time()
        if transaction_type == "create_group":
            execution_times[id] = end_time - start_time
            print(f"Thread {id} time (group creation): {end_time - start_time}")
        return nonce
    except Exception as error:
        handle_error(id=id, error=error)


def create_projects(id: int, addr: str, private_key: str, nonce: int, n_projects: int):
    try:
        start_time = time.time()
        print(f"Creating {n_projects} projects by thread {id}...")
        for i in range(n_projects):
            nonce += 1
            approveTokenFee(
                2000, nonce=nonce, addr=addr, private_key=private_key, id=id
            )
            nonce += 1
            createTransaction(
                contract.functions.createProject,
                f"group{id}_0",
                f"project{id}_{i}",
                nonce=nonce,
                wait=True,
                addr=addr,
                private_key=private_key,
                key="create_project",
                id=id,
            )
        end_time = time.time()
        if transaction_type == "create_project":
            execution_times[id] = end_time - start_time
            print(f"Thread {id} time (project creation): {end_time - start_time}")
        return nonce
    except Exception as error:
        handle_error(id=id, error=error)


def create_projects_with_names(
    id: int, addr: str, private_key: str, nonce: int, names: list
):
    try:
        start_time = time.time()
        print(f"Creating {len(names)} projects by thread {id}...")
        for i in names:
            nonce += 1
            approveTokenFee(
                2000, nonce=nonce, addr=addr, private_key=private_key, id=id
            )
            nonce += 1
            createTransaction(
                contract.functions.createProject,
                f"group{id}_0",
                i,
                nonce=nonce,
                wait=True,
                addr=addr,
                private_key=private_key,
                key="create_project",
                id=id,
            )

        end_time = time.time()
        execution_times[id] = end_time - start_time
        print(f"Thread {id} time (project creation): {end_time - start_time}")
        return nonce
    except Exception as error:
        handle_error(id=id, error=error)


def load_libraries(id: int, addr: str, private_key: str, nonce: int):
    try:
        with open("local/print_hi.js", "r") as f:
            file = f.read()
        print(f"Adding a version in the project print_hi...")
        CID1: str = ipfs.uploadFile(file)["cid"]
        nonce += 1
        approveTokenFee(1000, nonce=nonce, addr=addr, private_key=private_key, id=id)
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
            key="add_library",
            id=id,
        )

        with open("local/print_hi_n_times.js", "r") as f:
            file = f.read()
        print(f"Adding a version in the project print_hi_n_times...")

        CID2: str = ipfs.uploadFile(file)["cid"]
        nonce += 1
        approveTokenFee(1000, nonce=nonce, addr=addr, private_key=private_key, id=id)
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
            key="add_library",
            id=id,
        )
        return nonce
    except Exception as error:
        handle_error(id=id, error=error)


def check_dependencies_reliability(id: int, addr: str, private_key: str, nonce: int):
    try:
        CID = contract.functions.getProjectLastVersion("print_hi_n_times").call()
        nonce += 1
        receipt = createTransaction(
            contract.functions.getLibraryInformationWithLevel,
            CID,
            nonce=nonce,
            wait=True,
            addr=addr,
            private_key=private_key,
            key="get_library_information",
            id=id,
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
                    key="get_library_information",
                    id=id,
                )
                info = contract.events.LibraryInfo().processReceipt(receipt)[0]["args"]
                print(
                    f"{info.project}\nLast version: {info.version}\nReliability: {info.reliability}\nReliability level: {info.level}"
                )
        return nonce
    except Exception as error:
        handle_error(id=id, error=error)


def createTransaction(
    fun,
    *parameters,
    value=0,
    nonce: int,
    addr: str,
    private_key: str,
    key: str,
    id: int,
    wait: bool = False,
):  
    retry = 0
    while True:
        try:
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
            break
        except requests.exceptions.HTTPError as e:
            if retry >= 20:
                print("retry = 20")
                return
            sleep = (2 ** retry + 
                 random.uniform(0, 2))
            print(f"[{id}] HTTP retry in {fun}. Attempt number {retry + 1}")
            time.sleep(sleep*0.1)
            retry += 1
    retry = 0
    while True:
        try:
            if wait:
                receipt = w3.eth.wait_for_transaction_receipt(transaction_hash, timeout=80, poll_latency=0.6)
                transactions_cost[id] = transactions_cost.get(id, {key: []})
                transactions_cost[id][key] = transactions_cost[id].get(key, []) + [
                    (receipt["gasUsed"], receipt["effectiveGasPrice"])
                ]
                return receipt
            else:
                return 
        except requests.exceptions.HTTPError as e:
            if retry >= 20:
                return
            sleep = (2 ** retry + 
                 random.uniform(0, 2))
            print(f"[{id}] HTTP retry in wait_for_transaction_receipt. Attempt number {retry + 1}")
            time.sleep(sleep*0.1)
            retry += 1


def approveTokenFee(fee: int, nonce: int, addr: str, private_key: str, id: int):
    createTransaction(
        token_contract.functions.approve,
        contract.address,
        fee,
        nonce=nonce,
        addr=addr,
        private_key=private_key,
        wait=True,
        key="approve",
        id=id,
    )


def handle_error(id: int, error: Exception):
    print(f"Something went wrong in thread {id}")
    print(repr(error))
    if id not in failed_threads:
        failed_threads.append(id)


def process_transactions_cost(transaction_type):
    gas_costs = []
    gas_prices = []
    for id in transactions_cost:
        for transaction_keys in transactions_cost[id]:
            if transaction_keys == transaction_type:
                for transaction in transactions_cost[id][transaction_keys]:
                    gas_costs.append(transaction[0])
                    gas_prices.append(transaction[1])
    print("Gas cost min: " + str(min(gas_costs)))
    print("Gas cost max: " + str(max(gas_costs)))
    print("Gas cost mean: " + str(sum(gas_costs) / len(gas_costs)))
    print("Total gas cost: " + str(sum(gas_costs)))
    print()
    print("Gas price min: " + str(min(gas_prices)))
    print("Gas price max: " + str(max(gas_prices)))
    print("Gas price mean: " + str(sum(gas_prices) / len(gas_prices)))


def print_ex_time():
    while True:
        time.sleep(5)
        print(execution_times)

if __name__ == "__main__":
    keys: dict = parse_ganache_file(50)
    i: int = 0
    cmd = input(
        "Select one of the following:"
        + "\n1 - Groups creation test"
        + "\n2 - Projects creation test"
        + "\n3 - Check dependencies reliability test\n"
    )
    if cmd == "1":
        fun = thread_function_groups
        transaction_type = "create_group"
    elif cmd == "2":
        fun = thread_function_projects
        transaction_type = "create_project"
    elif cmd == "3":
        fun = thread_function_dependencies
        transaction_type = "get_library_information"
    else:
        print("Insert a valid command")
        quit()

    for addr in keys:
        t = Thread(target=fun, args=(i, addr, keys[addr]))
        i += 1
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    print(f"{len(failed_threads)} threads failed")
    print(len(execution_times.keys()))
    print(
        f"Execution time mean: {sum(execution_times.values())/len(execution_times.keys())}"
    )

    process_transactions_cost(transaction_type=transaction_type)
