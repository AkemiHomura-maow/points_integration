from brownie import LpSugar, VeSugar, PoolLpSugar, chain
from scripts.get_pair_info import fetch
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
import threading
import schedule
from flask import Flask, request, jsonify

app = Flask(__name__)

data = json.load(open('./config.json'))
pools = None

if chain.id == 10:
    data = data['op'] 
else:
    data = data['base']

lp_sugar = LpSugar.at(data['lp_sugar'])
pool_lp_sugar = PoolLpSugar.at(data['pool_lp_sugar'])
ve_sugar = VeSugar.at(data['ve_sugar'])
target = data['target']

# Fetch target token's balances in user's LP positions
def get_lp_balance(address, blk=None):
    global pools
    t = time.time()
    balance = 0
    results = pool_lp_sugar.positions(pools.index.tolist(), pools['is_cl'].tolist(), address, block_identifier=blk)

    for result in results:
        (id,lp,amount0, amount1, staked0, staked1, unstaked_earned0, unstaked_earned1) = result
        match = pools[pools.index == lp]
        if match.shape[0]:
            if match['token_pos'][0] == 0:
                balance += amount0 + staked0 + unstaked_earned0
            else:
                balance += amount1 + staked1 + unstaked_earned1
    print('LP bal run time', time.time() - t)
    return balance

# Fetch target token's balances in a given veNFT's unclaimed rewards
def fetch_nft_rewards(id, blk=None):
    total_amount = 0
    try:
        rewards = lp_sugar.rewards(4000, 0, id, block_identifier=blk)
    except:
        print(id)
        breakpoint()
    for reward in rewards:
        amt, token = reward[2], reward[3]
        if token == target:
            total_amount += amt
    return total_amount

# Fetch target token's balances in user's unclaimed rewards
def get_unclaimed_voting_rewards(address, blk=None):
    t = time.time()
    amount = 0
    # First fetch all the venft ids held by the user 
    results = ve_sugar.byAccount(address, block_identifier=blk)
    nft_ids = [res[0] for res in results]

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Then query unclaimed rewards for each nft
        futures = {executor.submit(fetch_nft_rewards, id, blk): id for id in nft_ids}
        for future in as_completed(futures):
            amount += future.result()
    print('veNFT Rewards bal run time', time.time() - t)
    return amount

def _get_balance(address, blk):
    t = time.time()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_lp_balance, address, blk), executor.submit(get_unclaimed_voting_rewards, address, blk)]
        results = [future.result() for future in futures]
    print(results[0]/1e18, results[1]/1e18)
    print('Total run time', time.time() - t)
    return sum(results)


# Fetch pool data every 1 hour
def fetch_pools():
    global pools
    pools = fetch(lp_sugar, target)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(3600).seconds.do(fetch_pools)
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()
fetch_pools()


# Flask API logics
def is_valid_eth_address(address):
    """ Simple check to validate Ethereum addresses """
    if address.startswith('0x') and len(address) == 42:
        return True
    return False

@app.route('/getBalance', methods=['GET'])
def get_balance():
    eth_address = request.args.get('address', None)
    blk = request.args.get('block', None)
    blk = int(blk) if blk is not None else None
    
    if not eth_address or not is_valid_eth_address(eth_address):
        return jsonify({"error": "Invalid or missing address"}), 400

    response_data = {
        "address": eth_address,
        "balance": _get_balance(eth_address, blk)
    }
    return jsonify(response_data), 200

app.run(debug=True)

def main():
    pass