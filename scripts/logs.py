from brownie import web3

def fetch_logs(event_signature, start_block, end_block, contracts=[]):
    return web3.eth.getLogs({
        'fromBlock': start_block,
        'toBlock': end_block,
        'topics': [event_signature],
        'address': contracts
    })
