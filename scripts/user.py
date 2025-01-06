from scripts.logs import fetch_logs
import re
from eth_abi import decode
from collections import defaultdict, Counter
from brownie import chain

TRANSFER_TOPIC0 = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

last_fetched_blk = 0
transfers = []
pools = None

def fetch_v2_pool_transfers(from_blk, end_blk, contracts):
    out = []
    from_block, to_block = from_blk, end_blk
    while True:
        print(from_block, to_block)
        try:
            results = fetch_logs(TRANSFER_TOPIC0, from_block, to_block, contracts)
            for res in results:
                pool = res.address
                from_addr = decode(['address'],res.topics[1])[0]
                to_addr = decode(['address'],res.topics[2])[0]
                amt = decode(['uint256'], bytes.fromhex(res.data.hex()[2:]))[0]
                out.append((pool, res.blockNumber, from_addr, to_addr, amt))
            if to_block == end_blk:
                return out
            from_block = to_block + 1
            to_block = end_blk
        except Exception as e:
            print(e)
            error_dict = eval(str(e)) 
            match = re.search(r', (0x[a-fA-F0-9]+)\]', error_dict.get("message", ""))
            if match:
                to_block = int(match.group(1), 16)

def refresh_pool_transfers():
    global last_fetched_blk, pools, transfers
    from_blk, to_blk = last_fetched_blk, chain.height
    transfers.extend(fetch_v2_pool_transfers(from_blk, to_blk, pools.index.to_list()))
    last_fetched_blk = to_blk

def get_v2_lps(snapshot_blk=None):
    balances = defaultdict(Counter)
    for transfer in transfers:
        pool, blk, from_addr, to_addr, amt = transfer
        if (snapshot_blk is not None and blk <= snapshot_blk) or snapshot_blk is None:
            gauge = pools.loc[pool]['gauge']
            if to_addr != '0x0000000000000000000000000000000000000001':
                if gauge != '0x0000000000000000000000000000000000000000':
                    if from_addr == gauge or to_addr == gauge:
                        continue
                balances[pool][from_addr] -= amt
                balances[pool][to_addr] += amt

    lps = set()
    for pool, pool_balances in balances.items():
        for usr, usr_bal in pool_balances.items():
            if usr_bal > 0:
                lps.add(usr)
    
    return list(lps)
