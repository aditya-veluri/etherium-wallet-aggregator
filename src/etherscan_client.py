import time
from datetime import date
import requests
import pandas as pd
from rate_limiter import RateLimiter
from utils import UtilityMethods as uM


class EtherscanClient:
    BASE_URL = "https://api.etherscan.io/api"
    MAX_REQUESTS_PER_SEC = 5
    TOKEN_REFILL_INTERVAL = 1  # seconds

    # start and end dates for the data retrieval
    # Can be externalized as method parameters or as ENV variables
    START_DATE = date(2016, 1, 1)
    END_DATE = date(2025, 3, 31)

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(max_requests=self.MAX_REQUESTS_PER_SEC, refill_interval=self.TOKEN_REFILL_INTERVAL)

    def _fetch(self, action: str, address: str, start_block=0, end_block=99999999) -> list:
        self.rate_limiter.acquire()

        params = {
            "module": "account",
            "action": action,
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
            "apikey": self.api_key
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if data["status"] != "1":
                print(f"Warning: No data found for action {action}. Message: {data.get('message')}")
                return []
            return data["result"]
        except Exception as e:
            print(f"Error fetching {action} for {address}: {e}")
            return []

    def _get_block_number_by_timestamp(self, timestamp: int, closest="before") -> int:
        self.rate_limiter.acquire()

        params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": closest,
            "apikey": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return int(response.json()["result"])

    def get_normal_transactions(self, address: str, start_block=0, end_block=99999999) -> list:
        return self._fetch("txlist", address, start_block, end_block)

    def get_internal_transactions(self, address: str, start_block=0, end_block=99999999) -> list:
        return self._fetch("txlistinternal", address, start_block, end_block)

    def get_erc20_transfers(self, address: str, start_block=0, end_block=99999999) -> list:
        return self._fetch("tokentx", address, start_block, end_block)

    def get_erc721_transfers(self, address: str, start_block=0, end_block=99999999) -> list:
        return self._fetch("tokennfttx", address, start_block, end_block)

    def get_all_transactions(self, address: str) -> pd.DataFrame:
        print("Fetching all transactions...")
        for start_ts, end_ts in uM.get_date_range_in_batches(self.START_DATE, self.END_DATE):
            start_block = self._get_block_number_by_timestamp(start_ts, "after")
            end_block = self._get_block_number_by_timestamp(end_ts, "before")

            print("Fetching normal transactions...")
            normal = self.get_normal_transactions(address, start_block, end_block)

            print("Fetching internal transactions...")
            internal = self.get_internal_transactions(address, start_block, end_block)

            print("Fetching token transactions...")
            erc20 = self.get_erc20_transfers(address, start_block, end_block)

            print("Fetching NFT transactions...")
            erc721 = self.get_erc721_transfers(address, start_block, end_block)

            df_normal = pd.DataFrame(normal)
            df_internal = pd.DataFrame(internal)
            df_erc20 = pd.DataFrame(erc20)
            df_erc721 = pd.DataFrame(erc721)

            # Add a column to identify type
            df_normal["tx_type"] = "normal"
            df_internal["tx_type"] = "internal"
            df_erc20["tx_type"] = "erc20"
            df_erc721["tx_type"] = "erc721"

            # Align columns before union
            common_cols = set(df_normal.columns) | set(df_internal.columns) | set(df_erc20.columns) | set(df_erc721.columns)
            all_dfs = [df.reindex(columns=common_cols) for df in [df_normal, df_internal, df_erc20, df_erc721]]

            combined_df = pd.concat(all_dfs, ignore_index=True)
            yield combined_df

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        required_cols = ["Transaction Hash", "Date & Time", "From Address", "To Address", "Transaction Type",
                         "Asset Contract Address", "Asset Symbol / Name", "Token ID", "Value / Amount", "Gas Fee (ETH)"]

        rename_mapping = {
            "hash": "Transaction Hash",
            "timeStamp": "Date & Time",
            "from": "From Address",
            "to": "To Address",
            "tx_type": "Transaction Type",
            "contractAddress": "Asset Contract Address",
            "tokenSymbol": "Asset Symbol / Name",
            "tokenID": "Token ID",
            "value": "Value / Amount",
            "gasPrice": "Gas Fee (ETH)"
        }

        df = df.rename(columns=rename_mapping)
        missing_cols = [col for col in required_cols if col not in list(df.columns)]
        for missing_col in missing_cols:
            df[missing_col] = ""

        return df[required_cols]
