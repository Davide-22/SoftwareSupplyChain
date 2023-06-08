import subprocess
import sys

if __name__ == "__main__":
    try:
        n_accounts = sys.argv[1]
        a = subprocess.run(
            ["ganache", "--miner.blockTime=1", f"--wallet.totalAccounts={n_accounts}", ">", "ganache.txt"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except:
        print("Usage: python start_test_blockchain.py <number of accounts>")
