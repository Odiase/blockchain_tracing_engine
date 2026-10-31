"""
This module contains functions that are used in the chain_trace.py module.
These functions include utility functions for converting values, making API calls,
and other helper functions that are used throughout the chain_trace module.
The functions in this module are designed to be reusable and modular,
allowing for easy maintenance and scalability of the codebase.
"""
from typing import Union
from web3 import Web3

# local imports
from .constants import (
    ERC_20_ABI,
    ETHEREUM_MAINNET_ENDPOINT
)



def get_web3_instance(chain_name: str) -> Union[Web3, None]:
    """
    This function returns a Web3 instance connected to the specified blockchain network.

    Returns:
        A Web3 instance connected to the specified blockchain network.
    """
    try:
        # Connect to the mainnet
        w3 = Web3(Web3.HTTPProvider(ETHEREUM_MAINNET_ENDPOINT))
        if w3.is_connected():
            return w3
        return None    
    except Exception as e:
        print(f"Error connecting to {chain_name}: {e}")
        return None


def get_token_balance(
    chain_name: str,
    contract_address: str,
    address: str
) -> Union[int, None]:
    """
    Gets the token balance of a given address for a specific ERC-20 token.
    
    Args:
        chain_name (str): The name of the blockchain network (e.g "Ethereum Mainnet").
        contract_address (str): The address of the ERC-20 token contract.
        address (str): The address for which to check the token balance.
    
    Returns:
        The token balance of the specified address for the given ERC-20 token.
    """
    web3 = get_web3_instance(chain_name)

    if web3 is None:
        print(f"Failed to connect to {chain_name}.")
        return None
    
    try:         
        # Validate contract address and wallet address
        if not web3.is_address(contract_address):
            print(f"Invalid contract address: {contract_address}")
            return None
        
        if not web3.is_address(address):
            print(f"Invalid wallet address: {address}")
            return None
        
        # Normalize addresses to checksum format
        contract_address = web3.to_checksum_address(contract_address)
        address = web3.to_checksum_address(address)
    except Exception as e:
        print(f"Error validating addresses: {e}")
        return None

    # create erc-20 contract instance.
    contract = web3.eth.contract(address=contract_address, abi=ERC_20_ABI)
    
    # Fetch data
    raw_balance = contract.functions.balanceOf(address).call()
    token_decimals = contract.functions.decimals().call()
    
    balance = raw_balance / (10**token_decimals)
    return balance
    



# balance = get_token_balance(
#     chain_name="Ethereum Mainnet",
#     contract_address="0xdac17f958d2ee523a2206206994597c13d831ec7",  # 
#     address="0x560B0a1bc3e23AE1FA7DC18323229673173d2e7a"
# )

# print(f"Token balance: {balance}")