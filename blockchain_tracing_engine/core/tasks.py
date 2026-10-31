from celery import shared_task
from .chain_trace import ChainTrace
import time


@shared_task
def run_chain_trace(trace_params: dict):
    chain_trace = ChainTrace(
        target_address=trace_params.get('target_wallet_address'),
        victim_address=trace_params.get('victim_wallet_address'),
        transaction_hash=trace_params.get('transaction_hash'),
        start_date=trace_params.get('investigation_start_date'),
        end_date=trace_params.get('investigation_end_date')
    )
    result = chain_trace.run()

    return result
