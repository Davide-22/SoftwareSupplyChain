from web3 import Web3, exceptions
from utils.ipfs import IPFS
from utils.check_dependencies import getDependencies


class Transactions:
    def __init__(
        self, w3: Web3, chain_id: int, addr: str, private_key: str, contract, token_contract, ipfs: IPFS 
    ):
        self.w3 = w3
        self.chain_id = chain_id
        self.addr = addr
        self.private_key = private_key
        self.contract = contract
        self.token_contract = token_contract
        self.ipfs = ipfs

    def addDeveloper(self):
        email: str = input("Insert your email: ")
        print("Registering as a developer...")
        try:
            self.approveTokenFee(3000)
            self.createTransaction(self.contract.functions.addDeveloper, email)
            print(f"Registered as a developer with email {email}\n")
        except exceptions.SolidityError as error:
            self.approveTokenFee(0)
            print(str(error)[70:], end="\n")

    def createGroup(self):
        group_name: str = input("Insert the group name: ")
        print("Creating a group...")
        try:
            self.approveTokenFee(2000)
            self.createTransaction(self.contract.functions.createGroup, group_name)
            print(f"Group {group_name} created\n")
        except exceptions.SolidityError as error:
            self.approveTokenFee(0)
            print(str(error)[70:], end="\n")

    def createProject(self):
        group_name: str = input(
            "Insert the name of the group in which you want to create a project: "
        )
        project_name: str = input("Insert the project name: ")
        print("Creating a project...")
        try:
            self.approveTokenFee(2000)
            self.createTransaction(
                self.contract.functions.createProject, group_name, project_name
            )
            print(f"Project {project_name} created\n")
        except exceptions.SolidityError as error:
            self.approveTokenFee(0)
            print(str(error)[70:], end="\n")

    def requestGroupAccess(self):
        group_name: str = input("Insert the name of the group that you want to join: ")
        print("Processing the request...")
        try:
            self.createTransaction(
                self.contract.functions.requestGroupAccess, group_name
            )
            print(f"The request to join the {group_name} group has been registered\n")
        except exceptions.SolidityError as error:
            print(str(error)[70:], end="\n")

    def acceptGroupRequest(self):
        group_name: str = input("Insert the name of the group: ")
        addr: str = input("Insert the address of the developer: ")
        print("Accepting the request...")
        try:
            self.createTransaction(
                self.contract.functions.acceptGroupRequest, group_name, addr
            )
            print(f"{addr} has been accepted in the {group_name} group\n")
        except exceptions.SolidityError as error:
            print(str(error)[70:], end="\n")

    def addLibrary(self):
        project_name: str = input("Insert the name of the project: ")
        path = input("Insert the path of the file: ")
        version: str = input("Insert the version of the library: ")
        dependencies: list = (
            input("Insert the list of the CID of the dependencies (comma separated): ")
            .strip()
            .split(",")
        )
        print("Adding the library...")
        try:
            with open(path, "r") as f:
                file = f.read()
        except FileNotFoundError:
            print("Wrong path")

        CID: str = self.ipfs.uploadFile(file)["cid"]
        try:
            self.approveTokenFee(1000)
            self.createTransaction(
                self.contract.functions.addLibrary,
                project_name,
                CID,
                version,
                dependencies,
            )
            print(f"The library has been added\n")
        except exceptions.SolidityError as error:
            self.approveTokenFee(0)
            print(str(error)[70:], end="\n")

    def voteDeveloper(self):
        developer: str = input("Insert the address of the developer: ")
        print("Voting the developer...")
        try:
            self.createTransaction(
                self.contract.functions.voteDeveloper,
                (developer),
            )
            print(f"The developer has been voted\n")
        except exceptions.SolidityError as error:
            print(str(error)[70:], end="\n")

    def reportDeveloper(self):
        developer: str = input("Insert the address of the developer: ")
        print("Reporting the developer...")
        try:
            self.createTransaction(
                self.contract.functions.reportDeveloper,
                developer,
            )
            print(f"The developer has been reported\n")
        except exceptions.SolidityError as error:
            print(str(error)[70:], end="\n")

    def updateReliability(self):
        print("Updating the reliability...")
        try:
            self.createTransaction(self.contract.functions.updateReliability)
            print(f"The reliability has been updated\n")
        except exceptions.SolidityError as error:
            print(str(error)[70:], end="\n")

    def changeAdmin(self):
        new_admin: str = input("Insert the address of the new admin: ")
        group_name: str = input("Insert the name of the group: ")
        print("Changing the admin...")
        try:
            self.createTransaction(
                self.contract.functions.reportDeveloper, new_admin, group_name
            )
            print(f"The admin has been changed\n")
        except exceptions.SolidityError as error:
            print(str(error)[70:], end="\n")

    def getDependenciesInformation(self):
        name = input("Insert the name of the library: ")
        try:
            CID = self.contract.functions.getProjectLastVersion(name).call()

            receipt = self.createTransaction(
                self.contract.functions.getLibraryInformationWithLevel,
                CID,
            )
            info = self.contract.events.LibraryInfo().processReceipt(receipt)[0]["args"]
            print(
                f"{info.project}\nLast version: {info.version}\nReliability: {info.reliability}\nReliability level: {info.level}"
            )
            dependencies = getDependencies(name)
            print(f"{name} dependencies:\n")
            for key in dependencies:
                if dependencies[key][0] == "^" or dependencies[key][0] == "~":
                    dependencies[key] = dependencies[key][1:]
                CIDs = self.contract.functions.getProjectVersions(key).call()
                for CID in CIDs:
                    receipt = self.createTransaction(
                        self.contract.functions.getLibraryInformationWithLevel,
                        CID,
                    )
                    info = self.contract.events.LibraryInfo().processReceipt(receipt)[
                        0
                    ]["args"]
                    if info.version == dependencies[key]:
                        print(
                            f"{info.project}\nLast version: {info.version}\nReliability: {info.reliability}\nReliability level: {info.level}\n"
                        )
                        break
        except:
            print("Insert a valid name")

    def buyTokens(self):
        tokens: str = input("Insert the number of tokens to buy: ")
        print("Buying tokens...")
        try:
            receipt = self.createTransaction(
                self.contract.functions.buyTokens, value=int(tokens)
            )
            print(f"{tokens} tokens have been bought\n")
        except exceptions.SolidityError as error:
            print(str(error)[70:], end="\n")
    
    def buyReliability(self):
        reliability: int = int(input("Insert the amount of reliability to buy: "))
        print("Buying reliability...")
        try:
            reliability_cost: int = int(self.contract.functions.reliability_cost().call())
            self.approveTokenFee(reliability*reliability_cost)
            receipt = self.createTransaction(
                self.contract.functions.buyReliability, reliability
            )
            print(f"{reliability} reliability has been bought\n")
        except exceptions.SolidityError as error:
            self.approveTokenFee(0)
            print(str(error)[70:], end="\n")

    def createTransaction(self, fun, *parameters, value=0):
        nonce: int = self.w3.eth.getTransactionCount(self.addr)
        transaction = fun(*parameters).buildTransaction(
            {
                "chainId": self.chain_id,
                "from": self.addr,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce,
                "value": value,
            }
        )
        signed_transaction = self.w3.eth.account.sign_transaction(
            transaction, private_key=self.private_key
        )
        transaction_hash = self.w3.eth.send_raw_transaction(
            signed_transaction.rawTransaction
        )
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        return tx_receipt
    
    def approveTokenFee(self, fee):
        receipt = self.createTransaction(
                self.token_contract.functions.approve, self.contract.address, fee
        )
