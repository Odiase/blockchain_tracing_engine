"""
blockchain_tracing_engine.core.GRAPH_DB_COMMANDS

This file contains the commands to interact with the graph database (neo4j)
to store and query the blockchain data for tracing purposes.
"""
import logging
import os
from pathlib import Path
from typing import Optional, Any

from dotenv import read_dotenv
from neo4j import GraphDatabase

# load environment vairables
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
env_path = project_root / '.env'
read_dotenv(dotenv=env_path)

# connection details
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
DB_NAME = os.getenv("NEO4J_DB_NAME", "alphadb")




class DBManager:
    def __init__(self):
        """Initializes the DBManager instance and establishes a connection
            to the neo4j database.
        """
        try:
            
            self.driver = GraphDatabase.driver(uri=URI, auth=AUTH)
            # verify the connection to the database. if its not successful,
            # it will raise an exception.
            self.driver.verify_connectivity(database=DB_NAME)
        except Exception as e:
            print("Error occuren whiule initializing the neo4j database : ", e)
            self.driver = None
    
    def close_connection(self) -> bool:
        """Closes the connection to the neo4j database"""
        if self.driver is not None:
            try:
                self.driver.close()
                return True
            except Exception as e:
                return False
        return False
    
    
    def create_wallet_node(
        self,
        address: str
    ) -> bool:
        """
        Creates a wallet mode in neo4j database with the given address as a property.
        
        Args:
            address (str): the address that will be used as a property for the wallet node
        
        Returns:
            True if the node is successfully created, False if it is not.
        """
        if self.driver is None:
            return False

        try:
            query = """
                MERGE (w:Wallet {address: $address})
                """
            summary = self.driver.execute_query(
                query,
                parameters_={
                    "address" : address.lower()
                },
                database_=DB_NAME
            )
            return True
        except Exception as e:
            return False

    
    def create_victim_scammer_relationship(
        self,
        victim_address: str,
        scammer_address: str,
        transaction_details: dict
    ) -> bool:
        """
        Creates the relationship between the victim and the scammer in the neo4j database.
        
        Args:
            victim_address (str): the address of the victim wallet.
            scammer_address (str): the address of the scammer wallet.
            transaction_details (dict): contains crucial details about the transaction between
                                        the victim and the scammer, such as transaction_hash,
                                        value, timeStamp, etc.
        
        Returns:
            True if the nodes and the relationship are successfully created, False if they are not.
        """
        
        if self.driver is None:
            return False
        
        try:
            query = """
            MERGE (v:Wallet {address: $victim_address})
            MERGE (s:Wallet {address: $scammer_address})

            MERGE (v)-[:SENT {
                transaction_hash: $tx_hash,
                value: $tx_value,
                timeStamp: $tx_time
            }]->(s)
            """

            # 2. Pass your variables securely as parameters
            summary = self.driver.execute_query(
                query,
                parameters_={
                    "victim_address": victim_address.lower(),
                    "scammer_address": scammer_address.lower(),
                    "tx_hash": transaction_details.get('hash'),
                    "tx_value": transaction_details.get('value'),
                    "tx_time": transaction_details.get('timeStamp')
                },
                database_=DB_NAME
            )
            print("Victim-Scammer Relationship Created")
            return True
        except Exception as e:
            print("Error occured while creating scammer victim relationship : ", e)
            return False
    
    
    def create_exchange_wallet_node():
        pass
    
    def create_relationship(
        self,
        from_address: str,
        to_address: str,
        tx_details: dict
    ):
        """
        Creates the relationship between the target wallet and the recipient wallet
        that it sent funds to.
        
        Args:
            from_address (str): the address of the wallet sending funds.
            to_address (str): the address of the wallet receiving funds.
            tx_details (dict): contains crucial details about the transaction
                                between the target and recipient.
        
        Returns:
            True if the nodes and the relationshps are successfully created, False if they are not.
        """
        if self.driver is None:
            return False
        
        try:
            query = """
            MERGE (target: Wallet {address: $from_address})
            MERGE (recipient: Wallet {address: $to_address})
            
            MERGE (target)-[:SENT{
                timeStamp: $tx_timeStamp,
                value: $tx_value,
                transaction_hash: $tx_hash
            }]->(recipient)
            """
            summary = self.driver.execute_query(
                query,
                parameters_={
                    "from_address" : from_address.lower(),
                    "to_address" : to_address.lower(),
                    "tx_timeStamp" : tx_details.get("timeStamp"),
                    "tx_value" : tx_details.get("value"),
                    "tx_hash" : tx_details.get("hash")
                },
                database_=DB_NAME
            )
            print("traget-recipient Relationship Created")
            return True
        except Exception as e:
            print(f"Error occured while creating relationship {e['error']}")
            return False


manager = DBManager()
print(manager.driver)