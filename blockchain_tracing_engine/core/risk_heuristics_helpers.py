# blockchain_tracing_engine/core/risk_heuristics_helpers.py
"""
This module contains helper functions that are used in the risk heuristics module.
"""

import os
from pathlib import Path
from typing import Union

from dotenv import read_dotenv
import requests

# local imports
from .helpers import get_token_balance
from .constants import (
    ERC20_USDT_DECIMALS,
    CHAINS,
    ETHERSCAN_API_ENDPOINT
)
from .risk_heuristics_constants import (
    RAPID_OUTFLOW_MAPPING,
    KNOWN_EXCHANGE_ADDRESSES,
)


# load environment vairables
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
env_path = project_root / '.env'
read_dotenv(dotenv=env_path)


def fetch_transactions(
    chain: str,
    address:str,
    contract_address: str
) -> list:
    """
    Fetches the ERC20 transactions of a given address on the Ethereum blockchain.
    Args:
        None
    Returns:
        a list of transactions for the given address on the specified blockchain.
    """
    chain_id = CHAINS[chain]

    payload_string = f"?apikey={os.getenv('ETHERSCAN_API_KEY')}&chainid={chain_id}&module=account&contractaddress={contract_address}&address={address}&action=tokentx&sort=desc"
    payload = ETHERSCAN_API_ENDPOINT + payload_string

    try:
        # send request to etherscan api
        response = requests.get(payload)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '0':
                print(f"No transactions found for address: {address} on chain: {chain}")
                return []
            return data['result']
        else:
            print(f"Failed to fetch token transfers. Status code: {response['result']}")
    except Exception as e:
        print(f"An error occurred while fetching the token transfers: {e}")


def fetch_target_address_transactions(
    chain_name: str,
    target_address: str,
    contract_address: str
) -> list:
    """
    Fetches the transactions of a given address on a specified blockchain.
    
    Args:
        chain_name (str): The name of the blockchain network (e.g "Ethereum Mainnet").
        target_address (str): The address for which to fetch transactions.
        contract_address (str): The address of the ERC-20 token contract.
    Returns:
        list: A list of transactions for the given address on the specified blockchain.
    """
    transactions = fetch_transactions(
        chain=chain_name,
        address=target_address,
        contract_address=contract_address
    )

    # sorting the transaction in ascending order.
    sorted_transactions = sorted(transactions, key=lambda x: int(x['timeStamp']))
    return sorted_transactions


def get_target_balance_before_victim_transaction(
    transactions: list | None,
    target_address: str,
    transaction_hash: str,
) -> tuple[float, float] | None:
    """
    This function calculates the estimated balance of the target address
    before the victim's transaction.
    
    Args:
        chain_name (str): The name of the blockchain network.
        contract_address (str): The address of the ERC-20 token contract.
        target_address (str): The address of the target(eg. the scammer's address).
        transaction_hash (str): The hash of the victim's transaction.
    Returns:
        Union[tuple(float, float), None]: A tuple containing the estimated balance
        of the target address before the victim's transaction and the amount sent by the victim,
        or None if there are no transactions.
    """
    # Get the target's transactions
    if not transactions:
        return None
    
    balance = 0
    amount_sent = 0
    incoming_value = 0  # amount of incoming usdt transactions to the target address.
    outgoing_value = 0  # amount of outgoing usdt transactions from the target address.
    
    # sorting the transaction in ascending order.
    transactions = sorted(transactions, key=lambda x: int(x['timeStamp']))
    
    # looping through the transactions to calculate the balance before the victim's transaction.
    for tx in transactions:
        if tx["hash"] == transaction_hash:
            amount_sent = float(tx["value"]) / ERC20_USDT_DECIMALS
            break
        
        if tx["to"] == target_address:
            incoming_value += float(tx["value"])
        if tx["from"] == target_address:
            outgoing_value += float(tx["value"])

    # dividing by token decimal to get correct balance. USDT has 6 decimals.
    balance = (incoming_value - outgoing_value) / ERC20_USDT_DECIMALS
    return (balance, amount_sent)


def assign_rapid_movement_score(rapid_ratio: float) -> str:
    """
    This function assigns a rapid movement score based on the rapid ratio.
    
    Args:
        rapid_ratio (float): The ratio of the total amount moved rapidly
                             to the amount sent by the victim.
    
    Returns:
        str: The assigned rapid movement score.
    """
    for threshold in sorted(RAPID_OUTFLOW_MAPPING.keys()):
        if rapid_ratio <= threshold:
            return RAPID_OUTFLOW_MAPPING[threshold]
    return RAPID_OUTFLOW_MAPPING[max(RAPID_OUTFLOW_MAPPING.keys())]


def is_exchange_address(address: str) -> bool:
    """
    This function checks if a given address is a known exchange address.
    
    Args:
        address (str): The address to check.
    
    Returns:
        bool: True if the address is a known exchange address, False otherwise.
    """
    return address.lower() in KNOWN_EXCHANGE_ADDRESSES


def get_exchange_from_address(address: str) -> Union[str, None]:
    """
    This function returns the exchange associated with
    the provided address.
    
    Args:
        address (str): This is the address that will be cross-referenced
                        against known exchange addresses.

    Returns:
        Union(str, None): The name of the exchange or None if not found.
    
    """
    
    if is_exchange_address(address):
        return KNOWN_EXCHANGE_ADDRESSES[address.lower()]
    

def get_victim_transaction(
    transactions: list,
    transaction_hash: str
) -> Union[dict, None]:
    """
    This function returns the details of the victim's transaction
    to the target.

    Args:
        transactions (list): this is the list of target's transactions.
        transaction_hash (str): the hash of the transaction between the victim and target.

    Returns:
        Union[dict, None]: The details of the transaction, or None if transaction
                            not found. 
    """

    if transactions == None or transaction_hash == None:
        return None

    victim_transaction = None

    sorted_transactions = sorted(transactions, key=lambda x: int(x['timeStamp']))    

    for tx in sorted_transactions:
        if tx["hash"].lower() == transaction_hash.lower():
            victim_transaction = tx

    return victim_transaction


def get_transactions_after_victim_tx(
    transactions: list,
    transaction_hash: str = None,
) -> Union[list, None]:
    """
    This helper function returns the list of transactions that
    have occured on the target's address after the victim's transaction.
    
    Args: transactions (list): The list of transactions to filter.
          transaction_hash (str): The hash of the victim's transaction.
    
    Returns: A list of transactions that have occured on the target's address
             after the victim's transaction.
    """
    if transaction_hash is None or not transactions:
        return None
    
    victim_txn_timestamp = None
    
    sorted_transactions = sorted(transactions, key=lambda x: int(x['timeStamp']))
    transactions_after_victim_txn = []
    
    for tx in sorted_transactions:
        if tx["hash"].lower() == transaction_hash.lower():
            victim_txn_timestamp = int(tx["timeStamp"])
            continue
        
        if victim_txn_timestamp != None:
            transactions_after_victim_txn.append(tx)
    
    return transactions_after_victim_txn


def get_outgoing_transactions_after_victim_tx(
    transactions: list,
    target_address: str,
) -> Union[list, None]:
    """
    This helper function returns the list of transactions that the target
    address has made after the victim's transaction.
    
    This is essentially every transactions where the target address is the sender
    and the transaction has occured after the victim's transaction.
    
    Args: transactions (list): The list of transactions after victim's transaction.
          target_address (str): The address of the target(scammer).
    
    Returns: A list of transactions that have occured on the target's address
             after the victim's transaction.
    """
    if not transactions:
        return None
    
    transactions_from_target_after_victim_txn = []
    
    for tx in transactions:
        if tx["from"].lower() == target_address.lower():
            transactions_from_target_after_victim_txn.append(tx)
    
    return transactions_from_target_after_victim_txn
