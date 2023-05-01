import os

from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv
from utils.transactions import Transactions
from utils.ipfs import IPFS

load_dotenv()

if __name__ == "__main__":
    with open("abi.json", "r") as file:
        abi = file.read()

    with open("token_abi.json", "r") as file:
        token_abi = file.read()

    w3: Web3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_ADDRESS")))
    chain_id: int = 1337
    addr: str = os.getenv("ADDRESS")
    private_key: str = os.getenv("PRIVATE_KEY")
    contract = w3.eth.contract(address=os.getenv("CONTRACT_ADDRESS"), abi=abi)
    token_contract = w3.eth.contract(address=os.getenv("TOKEN_CONTRACT_ADDRESS"), abi=token_abi)
    ipfs_auth_token: str = os.getenv("IPFS_AUTH_TOKEN")
    ipfs: IPFS = IPFS(contract=contract, ipfs_auth_token=ipfs_auth_token)
    transactions: Transactions = Transactions(
        w3=w3,
        chain_id=chain_id,
        addr=addr,
        private_key=private_key,
        contract=contract,
        token_contract=token_contract,
        ipfs=ipfs,
    )
    while True:
        cmd: str = input(
            """Select one of the following:
                1 - Register as a developer
                2 - Create a group
                3 - Create a project
                4 - Add a version of a library to a project
                5 - Get information about a developer
                6 - Get the address of a developer from the email
                7 - Get the number of developers
                8 - Get the number of groups
                9 - Get the number of projects
                10 - Get groups that a developer is a member of 
                11 - Get groups that a developer is an admin of 
                12 - Get the projects of a group
                13 - Get the group requests of a developer
                14 - Get the developers that requested to join a group
                15 - Get the versions of a library in a project
                16 - Get the last version of a library in a project
                17 - Get information about a library
                18 - Download a library
                19 - Request to join a group
                20 - Accept the join request of a developer
                21 - Vote a developer
                22 - Report a developer
                23 - Check the dependencies of a library and their reliability
                24 - Update your reliability
                25 - Appoint another developer as admin
                26 - Buy tokens
                27 - Buy reliability
                28 - Get the number of tokens of a developer
                q - Exit\n"""
        )
        if cmd == "1":
            transactions.addDeveloper()
        elif cmd == "2":
            transactions.createGroup()
        elif cmd == "3":
            transactions.createProject()
        elif cmd == "4":
            transactions.addLibrary()
        elif cmd == "5":
            a = input("Insert the address of the developer: ")
            try:
                info = contract.functions.getDeveloperInformation(a).call()
                print(
                    f"{a} information:\nEmail: {info[0]}\nReliability: {info[1]}\nRegistration date: {datetime.utcfromtimestamp(info[2]).strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
            except:
                print("Insert a valid address\n")
        elif cmd == "6":
            e = input("Insert the email of the developer: ")
            try:
                a = contract.functions.getDeveloperAddressFromEmail(e).call()
                print(f"The address of the developers is {a}")
            except:
                print("Insert a valid email\n")
        elif cmd == "7":
            n = contract.functions.devs_num().call()
            if n == 1:
                print(f"There is {n} developer\n")
            else:
                print(f"There are {n} developers\n")
        elif cmd == "8":
            n = contract.functions.groups_num().call()
            if n == 1:
                print(f"There is {n} group\n")
            else:
                print(f"There are {n} groups\n")
        elif cmd == "9":
            n = contract.functions.projects_num().call()
            if n == 1:
                print(f"There is {n} project\n")
            else:
                print(f"There are {n} projects\n")
        elif cmd == "10":
            a = input("Insert the address of the developer: ")
            try:
                g = contract.functions.getGroups(a).call()
                print(f"{a} is part of the following groups: {g}")
            except:
                print("Insert a valid address\n")
        elif cmd == "11":
            a = input("Insert the address of the developer: ")
            try:
                g = contract.functions.getGroups(a).call()
                print(f"{a} is admin of the following groups: {g}")
            except:
                print("Insert a valid address\n")
        elif cmd == "12":
            g = input("Insert the name of the group: ")
            try:
                p = contract.functions.getGroupProjects(g).call()
                print(f"In the group {g} there are the following projects: {p}")
            except:
                print("Insert a valid group name\n")
        elif cmd == "13":
            a = input("Insert the address of the developer: ")
            try:
                g = contract.functions.getGroupAccessRequests(a).call()
                print(f"The developer {a} requested to join the following groups: {g}")
            except:
                print("Insert a valid address\n")
        elif cmd == "14":
            g = input("Insert the name of the group: ")
            try:
                d = contract.functions.getToBeApproved(g).call()
                print(f"The following developers asked to join the group {g}: {d}")
            except:
                print("Insert a valid group name\n")
        elif cmd == "15":
            p = input("Insert the name of the project: ")
            try:
                v = contract.functions.getProjectVersions(p).call()
                print(
                    f"The following versions of the library are present in the project {p}: {v}"
                )
            except:
                print("Insert a valid project name\n")
        elif cmd == "16":
            p = input("Insert the name of the project: ")
            try:
                v = contract.functions.getProjectLastVersion(p).call()
                print(
                    f"The CID of the last version of the library of project {p} is {v}"
                )
            except:
                print("Insert a valid project name\n")
        elif cmd == "17":
            CID = input("Insert the CID of the library: ")
            try:
                info = contract.functions.getLibraryInformation(CID).call()
                print(info)
            except:
                print("Insert a valid CID\n")
        elif cmd == "18":
            CID = input("Insert the CID of the library: ")
            try:
                ipfs.downloadFileWithAllDependencies(CID=CID)
            except Exception as e:
                print(e)
        elif cmd == "19":
            transactions.requestGroupAccess()
        elif cmd == "20":
            try:
                transactions.acceptGroupRequest()
            except:
                print("Insert a valid address\n")
        elif cmd == "21":
            try:
                transactions.voteDeveloper()
            except:
                print("Insert a valid address\n")
        elif cmd == "22":
            try:
                transactions.reportDeveloper()
            except:
                print("Insert a valid address\n")
        elif cmd == "23":
            transactions.getDependenciesInformation()
        elif cmd == "24":
            transactions.updateReliability()
        elif cmd == "25":
            transactions.changeAdmin()
        elif cmd == "26":
            transactions.buyTokens()
        elif cmd == "27":
            transactions.buyReliability()
        elif cmd == "28":
            addr = input("Insert the address of the developer: ")
            try:
                balance = contract.functions.balanceOf(addr).call()
                print(balance)
            except:
                print("Insert a valid address\n")
        elif cmd == "q" or cmd == "Q":
            break
        else:
            print("Insert a valid command\n")
