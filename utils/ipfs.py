import requests


class IPFS:
    def __init__(self, contract, ipfs_auth_token: str):
        self.contract = contract
        self.ipfs_auth_token = ipfs_auth_token

    def uploadFile(self, file: str) -> dict:
        response = requests.post(
            "https://api.web3.storage/upload",
            data=file,
            headers={"Authorization": f"Bearer {self.ipfs_auth_token}"},
        )
        if "cid" in response.json():
            cid = response.json()["cid"]
            print(f"CID: {cid}")
        else:
            print(response.json())
        return response.json()

    def downloadFile(self, CID: str, name: str) -> int:
        response = requests.get(f"https://ipfs.io/ipfs/{CID}")
        if response.status_code == 200:
            with open(f"libraries/{name}", "w") as f:
                f.write(response.text)
        return response.status_code

    def downloadFileWithAllDependencies(self, CID: str):
        info = self.contract.functions.getLibraryInformation(CID).call()
        dependencies = info[2]
        status_code = self.downloadFile(CID=CID, name=info[1])
        if status_code == 200:
            print(
                f"The library {info[1]} (version {info[0]}) has been successfully downloaded"
            )
            if dependencies[0] != "":
                print(f"{info[1]} has the following dependencies: {dependencies}")
        else:
            print("Wrong CID")
            return
        for dep in dependencies:
            if dep != "":
                self.downloadFileWithAllDependencies(CID=dep)
