# blockchain_tracing_engine/core/risk_heuristics.py
"""
This module contains functions that implement various risk heuristics
for blockchain transactions.
"""
import json
from typing import Optional, Union


# local imports
from .risk_heuristics_helpers import (
    get_target_balance_before_victim_transaction,
    fetch_target_address_transactions,
    is_exchange_address,
    get_exchange_from_address,
    get_victim_transaction,
    get_outgoing_transactions_after_victim_tx
)
from .constants import (
    CHAIN,
    ERC20_USDT_DECIMALS,
    ERC20_USDT_CONTRACT_ADDRESS,
    FIVE_MINUTES,
    FIFTEEN_MINUTES,
    THIRTY_MINUTES,
    TWELVE_HOURS,
    EIGHT_HOURS,
    FOUR_HOURS,
    HOUR
)


class RiskHeuristic:
    """
    This class contains methods that implement various risk heuristics for
    blockchain transactions. Each method corresponds to a specific heuristic and
    returns a score or a set of details that can be used to assess the risk level
    of a transaction or an address.
    """
    
    def __init__(
        self,
        target_address: str,
        transaction_hash: str,
        transactions: list,
        outgoing_tx_after_victim_tx: list,
        victim_transaction: dict,
    ):
        self.target_address: str = target_address
        self.transaction_hash: str = transaction_hash
        self.target_transactions: list = transactions
        self.victim_transaction = victim_transaction
        self.outgoing_transactions_after_victim_tx = outgoing_tx_after_victim_tx
        self.wallet_investigated_count = 0
        try:
            self.target_balance_before_victim_txn, self.amount_sent_by_victim = get_target_balance_before_victim_transaction(
                self.target_transactions,
                target_address=target_address,
                transaction_hash=transaction_hash
            )
        except Exception as e:
            self.target_balance_before_victim_txn = None
            self.amount_sent_by_victim = None
    
    # Balance dominance heuristic
    def __determine_balance_dominance(self) -> Union[float, None]:
        """
        This heuristics checks the ratio/percentage of the amount sent by the 
        victim compared to the balance of the target address as at the time of the
        victim's transaction.
        
        If the amount sent is a significant portion of the target address's balance,
        it may indicate a higher chance of outgoing transactions from the target's wallet being
        malicious and most likely the victim's money.
        
        Args:
            None
        Returns:
            float: The ratio of the amount sent to the target address's balance.
        """
        # handle none values
        if self.target_balance_before_victim_txn is None or self.amount_sent_by_victim is None:
            return None

        # calculate balance dominance ratio and percentage
        if self.target_balance_before_victim_txn == 0 and self.amount_sent_by_victim > 0:
            return 100.0
        elif self.target_balance_before_victim_txn >= 0:
            balance_dominance_ratio = self.amount_sent_by_victim / self.target_balance_before_victim_txn
            balance_dominance_percentage = balance_dominance_ratio * 100
            return balance_dominance_percentage
        else:
            return None
        
        
    def __rapid_movement_heuristics(self) -> Union[dict, None]:
        """
        This heuristics measures velocity-weighted outflow from a target wallet after victim deposit. 
        If the target address sends out a significant portion of the received funds within a
        short time frame, it may indicate a higher likelihood of malicious activity.
        
        Args:
            None

        Returns:
            dict: A dictionary containing details about the rapid movement, or None if not detected.
        """

        victim_txn_timestamp = None
        amount_sent_by_victim = None

        if self.victim_transaction is None or "timeStamp" not in self.victim_transaction or "value" not in self.victim_transaction or self.outgoing_transactions_after_victim_tx is None:
            return None

        if not self.victim_transaction["to"].lower() == self.target_address.lower():
            return None

        victim_txn_timestamp = int(self.victim_transaction["timeStamp"])
        amount_sent_by_victim = float(self.victim_transaction["value"]) / ERC20_USDT_DECIMALS

        rapid_flow_value = 0
        weighted_flow_score = 0
        rapid_transactions = []

        # check for rapid movement of funds
        for tx in self.outgoing_transactions_after_victim_tx:
            if tx["from"].lower() == self.target_address.lower():
                tx_timestamp = int(tx["timeStamp"])
                delta = tx_timestamp - victim_txn_timestamp  # time difference

                # remember it was 30min, 5, 15minutes respectively for each condition
                if delta > 0 and delta <= TWELVE_HOURS:
                    # update the wallet investigated count
                    self.wallet_investigated_count += 1

                    # Time decay weighting (stonger means more suspicious)
                    weight = 0.4
                    if delta <= EIGHT_HOURS:
                        weight = 1.0
                    elif delta <= FOUR_HOURS:
                        weight = 0.7

                    amount = float(tx["value"]) / ERC20_USDT_DECIMALS
                    weighted_flow_score += amount * weight
                    rapid_flow_value += amount
                    rapid_transactions.append(tx)

    
        post_victim_balance = (
            self.target_balance_before_victim_txn + amount_sent_by_victim
        )
        
        # how much of the target's bal was sent by the victim
        victim_share_of_balance = amount_sent_by_victim / (
            post_victim_balance
        ) if (post_victim_balance) > 0 else 0
        
        # compare post-victim outflow to post-victim balance to get a sense of
        # how much of the victim's funds were rapidly moved out.
        rapid_drain_ratio = rapid_flow_value / (
            post_victim_balance
        ) if (post_victim_balance) > 0 else 0
        
        print(
            {
            "rapid_transaction_count": len(rapid_transactions),
            "raw_outflow": rapid_flow_value,
            "weighted_outflow_score": weighted_flow_score,
            "rapid_drain_ratio": rapid_drain_ratio,
            "victim_share_of_balance": victim_share_of_balance,
            "amount_sent_by_victim": amount_sent_by_victim,
            "post_victim_balance": post_victim_balance,
            }
        )

        return {
            "rapid_transaction_count": len(rapid_transactions),
            "raw_outflow": rapid_flow_value,
            "weighted_outflow_score": weighted_flow_score,
            "rapid_drain_ratio": rapid_drain_ratio,
            "victim_share_of_balance": victim_share_of_balance,
            "amount_sent_by_victim": amount_sent_by_victim,
            "post_victim_balance": post_victim_balance,
        }

    
    def __exchange_detection_heuristics(self) -> Optional[list] | None:
        """
        This heuristics checks if the target address interacts with a known
        or known exhange address after receiving funds from the victim.
        If the target address sends funds to an exchange shortly after receiving funds
        from the victim, it may indicate a higher likelihood of malicious activity.
        
        Args: 
            outgoing_transactions_from_target (list): This is the list of outgoing 
                                                        transactions from the target after
                                                        the victim's.
            transactions (list): All the target's transactions.
            transaction_hash (str): The hash of the victim's transaction to the target.

        Returns:
            (Optional[list] | None): A list of transactions made to known exchanges.

        """
        if not self.outgoing_transactions_after_victim_tx:
            return None
        
        if self.victim_transaction == None:
            return None
        
        transactions_sent_to_exchange = []
        amount_sent_by_victim = float(self.victim_transaction[
            "value"
        ]) / ERC20_USDT_DECIMALS

        # check transactions and cross reference them with known exchanges.
        for tx in self.outgoing_transactions_after_victim_tx:
            destination_wallet = tx["to"].lower()

            sent_to_exchange = is_exchange_address(destination_wallet)
            tx_timestamp = int(tx["timeStamp"])
            victim_timestamp = int(self.victim_transaction["timeStamp"])
            timestamp_within_30_mins = tx_timestamp >= victim_timestamp and \
                tx_timestamp - victim_timestamp <= THIRTY_MINUTES
            
            if sent_to_exchange and timestamp_within_30_mins:
                exchange_amount = float(tx["value"]) / ERC20_USDT_DECIMALS

                # zero division error check
                if amount_sent_by_victim == 0:
                    percentage_of_victim_funds = 0
                else:
                    # Calculate the raw percentage relative to what the victim sent
                    raw_percentage = (exchange_amount / amount_sent_by_victim) * 100
                    
                    # Cap it at 100% to avoid misleading percentages in a case where
                    # the targets wallert send more than what the victim sent
                    percentage_of_victim_funds = min(raw_percentage, 100.0)

                # payload
                tx_payload = {
                    "exchange_detected" : sent_to_exchange,
                    "exchange" : get_exchange_from_address(tx["to"]),
                    "exchange_address" : tx["to"],
                    "amount_sent" : exchange_amount,
                    "time_difference" : tx_timestamp - victim_timestamp,
                    "transaction_hash" : self.transaction_hash,
                    "percentage_of_victim_funds" : percentage_of_victim_funds
                }
                transactions_sent_to_exchange.append(tx_payload)
                continue
            
            # for EOA proxy ( in a case where the address is an EOA
            # generated by a known public exchange )
            
            # get transactions for this address
            destination_wallet_txs = fetch_target_address_transactions(
                chain_name=CHAIN,
                target_address=destination_wallet,
                contract_address=ERC20_USDT_CONTRACT_ADDRESS
            )
            # print(f"destination wallet txt: ", destination_wallet_txs)

            # with open("api_response.txt", "w", encoding="utf-8") as file:
            #     # Use response.text to get the raw content as a string
            #     file.write(f"'{destination_wallet_txs}'")
            
        
        return transactions_sent_to_exchange


    def calculate_wallet_risk(self) -> dict:
        """
        Computes a weighted risk score based on:
        - balance dominance (most important)
        - rapid movement
        - exchange detection
        
        Args:
            None

        Returns:
            A structured risk report with breakdown and final classification.
        """
        # weights (by importance)
        BALANCE_WEIGHT = 0.5
        RAPID_WEIGHT = 0.35
        EXCHANGE_WEIGHT = 0.15

        # BALANCE DOMINANCE SCORE
        balance_dominance = self.__determine_balance_dominance()

        if balance_dominance is None:
            balance_score = 0
        else:
            balance_score = min(balance_dominance, 100)


        # RAPID MOVEMENT SCORE
        rapid_movement_details = self.__rapid_movement_heuristics()

        if rapid_movement_details is None:
            rapid_score = 0
        else:
            post_victim_balance = rapid_movement_details.get(
                "post_victim_balance",
                0
            )

            if post_victim_balance > 0:
                rapid_ratio = (
                    rapid_movement_details["raw_outflow"] / post_victim_balance
                ) * 100
            else:
                rapid_ratio = 0

            rapid_score = min(rapid_ratio, 100)

       
        # EXCHANGE DETECTION SCORE
        exchange_detection = self.__exchange_detection_heuristics()

        exchange_score = 0
        if exchange_detection is not None:
            total_exchange_outflow_percentage = 0

            for tx in exchange_detection:
                total_exchange_outflow_percentage += tx.get(
                    "percentage_of_victim_funds", 0
                )

            exchange_score = min(total_exchange_outflow_percentage, 100)


        # FINAL WEIGHTED SCORE
        final_score = (
            (balance_score * BALANCE_WEIGHT) +
            (rapid_score * RAPID_WEIGHT) +
            (exchange_score * EXCHANGE_WEIGHT)
        )

        # RISK CLASSIFICATION
        if final_score >= 70:
            risk_level = "HIGH"
        elif final_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Payload
        return {
            "final_score": final_score,
            "risk_level": risk_level,
            "breakdown": {
                "balance_dominance_score": balance_score,
                "rapid_movement_score": rapid_score,
                "exchange_detection_score": exchange_score,
            },
            "wallets_investigated_count" : self.wallet_investigated_count,
            "transactions_processed" : len(self.outgoing_transactions_after_victim_tx)
        }
