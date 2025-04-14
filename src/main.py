from etherscan_client import EtherscanClient
from utils import UtilityMethods as uM
import argparse
from pathlib import Path

# Etherscan API key (allowed 5 requests / sec as part of free-tier plan)
API_KEY = "IRBK7VU4HC482G4ZFH7YZK5FWSJDA7X8Y8"

# Data folder
CUR_DIR = Path(__file__)
DATA_FOLDER = CUR_DIR.parent.parent / "data" / "output"
DATA_FOLDER.mkdir(parents=True, exist_ok=True)

parser = argparse.ArgumentParser(description="Process parameters for Transaction history retrieval of Etherium Wallets")
parser.add_argument("-a", "--address", help="Ethereum wallet address for which we want to pull the data")

args = parser.parse_args()
WALLET_ADDRESS = args.address


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = EtherscanClient(API_KEY)

    out_file_path = DATA_FOLDER / f"all_transactions_{WALLET_ADDRESS}.csv"
    uM.delete_file(out_file_path)

    write_header = True
    chunk = 1
    for all_txs in client.get_all_transactions(WALLET_ADDRESS):
        print(f"Chunk: {chunk} --- Total transactions: {len(all_txs)}")
        final_df = client.transform_df(all_txs)
        final_df.to_csv(out_file_path, mode='a', index=False, header=write_header)
        print(f"Chunk: {chunk} --- Output written to CSV")

        write_header = False
        chunk += 1
