from brownie import LpSugar, VotingRewardsHelper, PoolLpSugar, chain, interface
from scripts.get_pair_info import fetch
from concurrent.futures import ThreadPoolExecutor
import json
import time
import threading
import schedule
from flask import Flask, request, jsonify
from scripts.get_old_balance import get_old_balance
import scripts.user as usr

app = Flask(__name__)

data = json.load(open('./config.json'))
pools = None

chain_id = chain.id

if chain_id == 10:
    data = data['op'] 
    lp_sugar = LpSugar.at(data['lp_sugar'])
    port = 9000
else:
    data = data['base']
    lp_sugar = LpSugar.at(data['lp_sugar'])
    port = 9001

multicall = interface.IMulticall3('0xcA11bde05977b3631167028862bE2a173976CA11')    
pool_lp_sugar = PoolLpSugar.at(data['pool_lp_sugar'])
ve_rewards_helper = VotingRewardsHelper.at(data['ve_rewards_helper'])
target = data['target']

def get_lp_balances(addresses, pools, blk=None):
    """
    Fetch the target token's balances in the user's LP positions.

    Args:
        addresses ([str]): LPs' addresses
        blk (int, optional): The block number to fetch the data from. Defaults to None.

    Returns:
        [int]: The total balance of the target token in the user's LP positions.
    """

    t = time.time()
    balance = 0

    input_args = []

    for address in addresses:
        input_args.append([pool_lp_sugar.address, pool_lp_sugar.positions.encode_input(pools.index.tolist(), pools['is_cl'].tolist(), address)])

    raw_results = multicall.aggregate.call(input_args, block_identifier=blk)[1]
    results = [pool_lp_sugar.positions.decode_output(res) for res in raw_results]

    out_balances = []
    for result in results:
        balance = 0
        for res in result:
            (id, lp, amount0, amount1, staked0, staked1, unstaked_earned0, unstaked_earned1) = res
            match = pools[pools.index == lp]
            if match.shape[0]:
                if match['token_pos'][0] == 0:
                    balance += amount0 + staked0 + unstaked_earned0
                else:
                    balance += amount1 + staked1 + unstaked_earned1
        out_balances.append(balance)
    return out_balances


def get_unclaimed_voting_rewards(addresses, pools, blk=None):
    """
    Fetch the target token's balances in the user's unclaimed rewards.

    Args:
        address ([str]): LPs' addresses.
        blk (int, optional): The block number to fetch the data from. Defaults to None/latest block.

    Returns:
        [int]: The total amount of the target token in the user's unclaimed rewards.
    """
    t = time.time()

    input_args = []

    for address in addresses:
        input_args.append([ve_rewards_helper.address, ve_rewards_helper.fetch.encode_input(address,  ## User address
                                                        target,   ## Target token
                                                        0,        ## From nft_id
                                                        100,      ## To nft_id (included)
                                                        ## Fetch target token rewards from fee rewards contract & bribe rewards contract
                                                        [contract for contract in pools['fee_voting_reward'].tolist() + pools['bribe_voting_reward'].tolist() if contract != '0x0000000000000000000000000000000000000000'])])

    raw_results = multicall.aggregate.call(input_args, block_identifier=blk)[1]
    return [ve_rewards_helper.fetch.decode_output(res)[0] for res in raw_results]
    
def _get_new_balances(pools, addresses, blk):
    """
    Fetch the total balance of the target token in the user's LP positions and unclaimed rewards.

    Args:
        address (str): LPs' addresses.
        blk (int, optional): The block number to fetch the data from. 

    Returns:
        int: The total balance of the target token.
    """

    # t = time.time()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_lp_balances, addresses, pools, blk), executor.submit(get_unclaimed_voting_rewards, addresses, pools[pools['gauge_created_blk'] < blk], blk)]
        results = [future.result() for future in futures]
    out = [b0+b1 for b0, b1 in zip(results[0], results[1])]
    return out

def fetch_pools():
    """
    Fetch the pool data and update the global `pools` variable.
    """
    global pools
    pools = fetch(lp_sugar, target)
    # pools = pools[pools['fee_voting_reward'] != '0x0000000000000000000000000000000000000000']

def run_scheduler():
    """
    Run the scheduler to execute scheduled tasks.
    """
    while True:
        schedule.run_pending()
        time.sleep(1)

def _get_balances(addresses, blk):
    global pools
    tmp_pools = pools.copy()
    tmp_pools = tmp_pools[tmp_pools['pool_created_blk'] < blk]

    if (chain_id == 10 and blk > 121593546) or (chain_id != 10 and blk > 15998298):
        balances = _get_new_balances(tmp_pools, addresses, blk)
    elif chain_id != 10 and target.lower() == '0x04c0599ae5a44757c0af6f9ec3b93da8976c150a'.lower():
        balances = get_old_balance(tmp_pools.index.tolist(), addresses, blk)
    elif chain_id == 10 and target.lower() == '0x5a7facb970d094b6c7ff1df0ea68d99e6e73cbff'.lower():
        balances = get_old_balance(tmp_pools.index.tolist(), addresses, blk)

    return balances

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

    This endpoint retrieves a list of users based on the specified blockchain height (block). 
    If no block is provided, it retrieves users for the current height.

    Query Parameters:
        block (optional): An integer representing the blockchain height. Defaults to None.

    Returns:
        Response: JSON response containing a list of users.
    """
    blk = request.args.get('block', None)
    blk = int(blk) if blk is not None else None
    users = usr.get_lps(blk)
    response_data = {
        "users": users
    }
    return jsonify(response_data), 200

@app.route('/getBalances', methods=['GET'])
def get_balances():
    """
    Handle GET requests to the /getBalances endpoint.

    This endpoint retrieves the balances of specified users at a given blockchain height (block). 
    If no block is provided, it defaults to the current chain height. If no users are specified, 
    it retrieves balances for all users.

    Args:
        block (optional): An integer representing the blockchain height. Defaults to the current chain height.
        users (optional): A comma-separated string of user addresses. If not provided, retrieves balances for all users.

    Returns:
        Response: JSON response containing user addresses and their effective balances, sorted by balance in descending order.
    """
    blk = request.args.get('block', None)
    users_in = request.args.get('users', None)
    blk = int(blk) if blk is not None else chain.height
    t = time.time()
    if users_in is None:
        users = usr.get_lps(blk)
    else:
        users = users_in.split(',')

    bals = _get_balances(users, blk)
    
    print(round(time.time() - t,3))
    out = []
    for user, bal in zip(users, bals):
        if round(bal/1e18,3) > 0:
            out.append({'address': user, 'effective_balance': round(bal/1e18,3)})
    out = sorted(out, key=lambda item: item['effective_balance'], reverse=True)
    return jsonify(out), 200


schedule.every(3600).seconds.do(fetch_pools)
schedule.every(60).seconds.do(usr.refresh_pool_transfers)
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

fetch_pools()
usr.pools = pools
usr.refresh_pool_transfers()
app.run(host='0.0.0.0', port=port)





