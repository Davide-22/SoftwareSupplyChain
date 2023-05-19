# SoftwareSupplyChain

# Start the program
### Prerequisites
1. python 3 https://www.python.org/downloads/
2. Git https://git-scm.com/
3. Ganache https://trufflesuite.com/ganache/
4. Node.js https://nodejs.org/en 
5. npm-remote-ls https://www.npmjs.com/package/npm-remote-ls
6. An account on https://web3.storage/

### Start
First, create a workspace on Ganache.

Clone the repository:
```bash
git clone https://github.com/Davide-22/SoftwareSupplyChain.git
```
Enter in the folder:
```bash
cd SoftwareSupplyChain
```
Install the requirements:
```bash
pip install -r requirements.txt
```
Execute deploy.py:
```bash
python deploy.py
```
The script will ask for the wallett address and the private key. Both these information can be found in one of the wallet created on Ganache. Also, the blockchain address is on Ganache. Insted, the IPFS token can be created on https://web3.storage.

Execute call_contract.py:
```bash
python call_contract.py
```
