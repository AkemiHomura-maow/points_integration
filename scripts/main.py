from brownie import LpSugar, VotingRewardsHelper, PoolLpSugar, chain
from scripts.get_pair_info import fetch
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
import threading
import schedule
import requests
from flask import Flask, request, jsonify
from json import dumps

app = Flask(__name__)

data = json.load(open('./config.json'))
pools = None
chainbase_key = data['chainbase_key']

chain_id = chain.id

if chain_id == 10:
    data = data['op'] 
else:
    data = data['base']

lp_sugar = LpSugar.at(data['lp_sugar'])
pool_lp_sugar = PoolLpSugar.at(data['pool_lp_sugar'])
ve_rewards_helper = VotingRewardsHelper.at(data['ve_rewards_helper'])
target = data['target']
v2_router = data['v2_router']
cl_router = data['cl_router']
first_block = data['first_block']

def get_lp_balance(address, blk=None):
    """
    Fetch the target token's balances in the user's LP positions.

    Args:
        address (str): The user's Ethereum address.
        blk (int, optional): The block number to fetch the data from. Defaults to None.

    Returns:
        int: The total balance of the target token in the user's LP positions.
    """
    global pools
    t = time.time()
    balance = 0
    results = pool_lp_sugar.positions(pools.index.tolist(), pools['is_cl'].tolist(), address, block_identifier=blk)

    for result in results:
        (id, lp, amount0, amount1, staked0, staked1, unstaked_earned0, unstaked_earned1) = result
        match = pools[pools.index == lp]
        if match.shape[0]:
            if match['token_pos'][0] == 0:
                balance += amount0 + staked0 + unstaked_earned0
            else:
                balance += amount1 + staked1 + unstaked_earned1
    print('LP bal run time', time.time() - t)
    return balance


def get_unclaimed_voting_rewards(address, blk=None):
    """
    Fetch the target token's balances in the user's unclaimed rewards.

    Args:
        address (str): The user's address.
        blk (int, optional): The block number to fetch the data from. Defaults to None/latest block.

    Returns:
        int: The total amount of the target token in the user's unclaimed rewards.
    """
    t = time.time()
    amount, exhausted = ve_rewards_helper.fetch(address,  ## User address
                                                target,   ## Target token
                                                0,        ## From nft_id
                                                100,      ## To nft_id (included)
                                                ## Fetch target token rewards from fee rewards contract & bribe rewards contract
                                                pools['fee_voting_reward'].tolist() + pools['bribe_voting_reward'].tolist(), 
                                                block_identifier=blk)
    print('veNFT Rewards bal run time', time.time() - t)
    return amount

def _get_balance(address, blk):
    """
    Fetch the total balance of the target token in the user's LP positions and unclaimed rewards.

    Args:
        address (str): The user's Ethereum address.
        blk (int, optional): The block number to fetch the data from. Defaults to None/latest block.

    Returns:
        int: The total balance of the target token.
    """
    t = time.time()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_lp_balance, address, blk), executor.submit(get_unclaimed_voting_rewards, address, blk)]
        results = [future.result() for future in futures]
    print(results[0] / 1e18, results[1] / 1e18)
    print('Total run time', time.time() - t)
    return sum(results)

def fetch_pools():
    """
    Fetch the pool data and update the global `pools` variable.
    """
    global pools
    pools = fetch(lp_sugar, target)
    pools = pools[pools['fee_voting_reward'] != '0x0000000000000000000000000000000000000000']

def run_scheduler():
    """
    Run the scheduler to execute scheduled tasks.
    """
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
    """
    Validate Ethereum addresses.

    Args:
        address (str): The Ethereum address to validate.

    Returns:
        bool: True if the address is valid, False otherwise.
    """
    if address.startswith('0x') and len(address) == 42:
        return True
    return False

@app.route('/getBalance', methods=['GET'])
def get_balance():
    """
    Handle GET requests to the /getBalance endpoint.

    Args:
        None

    Returns:
        Response: JSON response containing the address and its balance or an error message.
    """
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

@app.route('/getPools', methods=['GET'])
def get_pools():
    """
    Handle GET requests to the /getPools endpoint.

    This endpoint retrieves information about pools, fee voting rewards and bribe voting reward contracts for the target token.

    Returns:
        Response: JSON response containing pools and their corresponding fee voting rewards and bribe voting reward contracts.
    """
    global pools
    out = pools[['fee_voting_reward', 'bribe_voting_reward']]
    response_data = json.loads(out.to_json(orient='table'))['data']

    return jsonify(response_data), 200

@app.route('/getUsers', methods=['GET'])
def get_users():
    """
    Handle GET requests to the /getUsers endpoint.

    Args:
        None, optional block

    Returns:
        Response: JSON response containing the users that have deposited into pools containing the target token.
    """

    blk = request.args.get('block', None)
    blk = int(blk) if blk is not None else None

    if chain_id == 10:
        query = "select distinct from_address from optimism.transactions where block_number > " + str(first_block) + " and ((input like '0x5a47ddc3%') or (input like '0xb5007d1f%') or (input like '0xb7e0d4c0%')) and ((to_address like '%" + v2_router[2:].lower() + "%') or (to_address like '%" + cl_router[2:].lower() + "%')) and (input like '%" + target[2:].lower() + "%')"
    else:
        query = "select distinct from_address from base.transactions where block_number > " + str(first_block) + " and ((input like '0x5a47ddc3%') or (input like '0xb5007d1f%') or (input like '0xb7e0d4c0%')) and ((to_address like '%" + v2_router[2:].lower() + "%') or (to_address like '%" + cl_router[2:].lower() + "%')) and (input like '%" + target[2:].lower() + "%')"
    
    if blk is not None:
        query += " and (block_number < " + str(blk) + ")"

    headers = {"accept": "application/json", "x-api-key": chainbase_key, "content-type": "application/json"}

    response = requests.post("https://api.chainbase.online/v1/dw/query", headers=headers, data=dumps({"query": query}))
    response = response.json()

    users = response['data']['result']

    response_data = {
        "users": users,
    }
    return jsonify(response_data), 200

app.run(debug=True)

def main():
    pass
