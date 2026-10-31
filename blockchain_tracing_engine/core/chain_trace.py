#blockchain_tracing_engine/core/chain_trace.py
"""
This module contains the ChainTrace class, which is responsible for
tracing the execution of transactions on the blockchain. It provides
methods to retrieve transaction details, trace the execution of transactions
and analyze the results of the traces. The ChainTrace class interacts with
the Etherscan API to fetch transaction data and uses various libraries to
perform the tracing and analysis.
"""

from collections import deque
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import requests
import time
from typing import Any, Union, Optional

from dotenv import read_dotenv
from web3 import Web3

# local imports
from .GRAPH_DB_COMMANDS import DBManager
from .fraud_risk_heuristics import RiskHeuristic
from .risk_heuristics_helpers import (
    get_victim_transaction,
    get_transactions_after_victim_tx,
    get_outgoing_transactions_after_victim_tx
)
from .constants import (
    CHAINS,
    CHAIN,
    ETHERSCAN_API_ENDPOINT,
    ERC20_USDT_CONTRACT_ADDRESS
)


# load environment vairables
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
env_path = project_root / '.env'
read_dotenv(dotenv=env_path)

# configure logging settings
logging.basicConfig(
    level=logging.DEBUG
)
# 1. Mute third-party noise (Run this BEFORE initializing drivers)
logging.getLogger("neo4j").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class ChainTrace:
    """
    The ChainTrace class is responsible for tracing the execution of transactions on the blockchain.
    It provides methods to retrieve transaction details, trace the execution of transactions
    and analyze the results of the traces. The ChainTrace class interacts with the Etherscan API
    to fetch transaction data and uses various libraries to perform the tracing and analysis.
    """
    
    def __init__(
        self,
        target_address: str,
        victim_address: str,
        transaction_hash: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ):
        """
        Initializes the ChainTrace instance and establishes a connection
        to the neo4j database using the DBManager class.
        """
        self.db_manager = DBManager()
        # Normalize addresses to checksum format
        self.target_address = Web3.to_checksum_address(target_address.lower())
        self.victim_address = Web3.to_checksum_address(victim_address.lower())
        self.victim_transaction_hash = transaction_hash
        self.chain = CHAIN
        self.chain_id = CHAINS.get(CHAIN)
        self.contract_address = ERC20_USDT_CONTRACT_ADDRESS
        self.etherscan_api = ETHERSCAN_API_ENDPOINT
        self.start_date =  datetime.combine(
            start_date,
            datetime.min.time(),
            tzinfo=timezone.utc
        )
        self.end_date = datetime.combine(
            end_date,
            datetime.min.time(),
            tzinfo=timezone.utc
        )
        self.target_transactions = list | None
        self.time_filtered_transactions: Optional[list[dict[str, Any]]] = None
        self.outgoing_txs_after_victim_tx: Optional[list[dict[str, Any]]] = None
        self.victim_tx: Optional[dict[str, Any]] = None

        logging.info("Inititialized ChainTrace instance for target address: %s, victim address: %s, transaction hash: %s", self.target_address, self.victim_address, self.victim_transaction_hash)


    def fetch_transactions(
        self
    ) -> list:
        """
        Fetches the ERC20 transactions of a given address on the Ethereum blockchain.

        Args:
            None
        Returns:
            a list of transactions for the given address on the specified blockchain.
        """
 
        payload_string = f"?apikey={os.getenv('ETHERSCAN_API_KEY')}&chainid={self.chain_id}&module=account&contractaddress={self.contract_address}&address={self.target_address}&action=tokentx&sort=desc"
        payload = self.etherscan_api + payload_string

        try:
            # send request to etherscan api
            response = requests.get(payload)

            if response.status_code == 200:
                data = response.json()
                if data['status'] == '0':
                    print(f"No transactions found for address: {self.target_address} on chain: {self.chain}")
                    return []
                result = data['result']
                self.target_transactions = result
                return result
            else:
                print(f"Failed to fetch token transfers. Status code: {response['result']}")
        except Exception as e:
            print(f"An error occurred while fetching the token transfers: {e}")
        
        logging.info("fetched transactions for target address")


    def filter_transactions_by_time(
        self
    ) -> list[dict[str, Any]]:
        """
        Retrieves transaction details within a specified time range.
        
        Args:
            None
        Returns:
            list[dict[str, Any]]: Transactions that fall within the specified time range.
        """
        transactions = self.fetch_transactions()

        # getting transactions within specified time range
        transactions_within_range = []
        _start_date = self.start_date.timestamp()
        _end_date = self.end_date.timestamp() if self.end_date is not None else datetime.now().timestamp()

        for tx in transactions:
            if int(tx["timeStamp"]) >= _start_date and int(tx["timeStamp"]) <= _end_date:
                new_tx = {
                    "timeStamp": tx["timeStamp"],
                    "hash": tx["hash"],
                    "from": tx["from"],
                    "to": tx["to"],
                    "tokenName": tx["tokenName"],
                    "tokenSymbol": tx["tokenSymbol"],
                    "value": tx["value"],
                }
                transactions_within_range.append(new_tx)

        self.time_filtered_transactions = transactions_within_range
        logging.info("filtered transactions by time for target address")
        return transactions_within_range
    
    
    def insert_victim_scammer_relationship(self) -> bool:
        """
        Creates the relationship between the victim and scammer in the neo4j database.
        
        Args:
            None
        
        Returns:
            True if the nodes and the relationships are successfully created, false if they are not.
        """
        
        logging.info("Inserting victim-scammer relationship for target address: %s", self.target_address)
        if not self.db_manager or not self.time_filtered_transactions:
            return False
        
        # get victim's transactions
        try:
            victim_transaction = get_victim_transaction(
                transactions=self.target_transactions,
                transaction_hash=self.victim_transaction_hash
            )
            self.victim_tx = victim_transaction
        except Exception as e:
            print(f"Error occurred while fetching victim transaction: {e}")
            return False
        
        if not victim_transaction:
            return False
        
        # create nodes and relationship in neo4j database
        try:
            created = self.db_manager.create_victim_scammer_relationship(
                victim_address=self.victim_address,
                scammer_address=self.target_address,
                transaction_details=victim_transaction
            )
        except Exception as e:
            print(f"Database error: {e}")
            created = False

        return created
    
    
    def insert_outgoing_relationships_after_victim_tx(
        self
    ) -> bool:
        """
        Creates the relationships between the target and the recipient wallets of
        the transactions.
        
        Args:
            None
        
        Returns:
            True if the nodes and the relationships are successfully created, false if they
            are not.
        """
        if not self.db_manager or not self.time_filtered_transactions:
            return False
        
        logging.info("Inserting outgoing relationships after victim transaction for target address: %s", self.target_address)
        try:
            # get outgoing txs after victim's
            if not self.outgoing_txs_after_victim_tx:
                transactions_after_victim_tx = get_transactions_after_victim_tx(
                    transactions=self.target_transactions,
                    transaction_hash=self.victim_transaction_hash
                )
                outgoing_transactions_after_victim_tx = get_outgoing_transactions_after_victim_tx(
                    transactions_after_victim_tx,
                    self.target_address
                )
                self.outgoing_txs_after_victim_tx = outgoing_transactions_after_victim_tx
            else:
                outgoing_transactions_after_victim_tx = self.outgoing_txs_after_victim_tx
            
            # create relationships in neo4j
            for tx in outgoing_transactions_after_victim_tx:
                # create wallet node
                recipient = tx["to"].lower()
                self.db_manager.create_wallet_node(recipient)
                
                # create relationship between target and recipient
                self.db_manager.create_relationship(
                    from_address=self.target_address,
                    to_address=recipient,
                    tx_details=tx
                )

            return True
        except Exception as e:
            print(f"Error occured while fetching outgoing txs: {e}")
            return False
    
    
    def run_heuristics(self) -> Union[bool, dict]:
        """
        Runs the heuristics to analyze the transaction graph and identify
        potential scams.
        """
        # create risk heuristics instance
        risk_heuristics = RiskHeuristic(
            self.target_address,
            self.victim_transaction_hash,
            self.target_transactions,
            self.outgoing_txs_after_victim_tx,
            self.victim_tx
        )
        
        # get heuristics details
        heuristics_details = risk_heuristics.calculate_wallet_risk()
        logging.info("Calculated wallet risk for target address: %s", self.target_address)
        
        return [heuristics_details is not None, heuristics_details]
    
    
    def run(self) -> Union[bool, dict]:
        """
        Runs the chain trace by executing the following steps:
        - get the transactions of the target address from the blockchain
        - filter the transaction with specified time frames.
        - get the victim's transaction details.
        - create the relationship between victim and scammer.
        - create the relationships between the target and the recipient wallets of
          the transactions that occured after the victim's transaction.
        - run the heuristics to analyze the transaction graph and identify
          potential scams.
          
        Args:
            None
        
        Returns:
            Union[bool, dict]: A tuple containing a boolean that shows if the risk heuristics were successfully calculated,
                                and a dictionary that contains the heuristics details.
        """
        try:
            # filter transactions by time
            self.filter_transactions_by_time()
            
            # insert victim-scammer relationship in neo4j database
            self.insert_victim_scammer_relationship()
            
            # insert relationships between target and recipient wallets in neo4j database
            self.insert_outgoing_relationships_after_victim_tx()
            
            # run heuristics to analyze the transaction graph and identify potential scams
            heuristics_details = self.run_heuristics()
            
            return heuristics_details
        except Exception as e:
            print(f"An error occurred while running the chain trace: {e}")
            return [False, None]
        


def main():
    """
    Runs a ChainTrace instance
    """
    test_address = "0x319028c5dd6e6bed00639e9ef536967de1117582" # gray's wallet
    victim_test_address = "0x2cff890f0378a11913b6129b2e97417a2c302680"
    test_transaction_hash = "0x210f4307fa13304eb91650ede0d1436f8c459f96bb640c3c7026bc9acd98e493"

    # create chaintrace instance
    chain_trace = ChainTrace(
        target_address=test_address,
        victim_address=victim_test_address,
        transaction_hash=test_transaction_hash,
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 6, 1)
    )

    heuristics_data = chain_trace.run()
    print(heuristics_data)


if __name__ == "__main__":
    main()
