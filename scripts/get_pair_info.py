import pandas as pd
from brownie import chain, interface
import json

data = json.load(open('./config.json'))
chain_id = chain.id
if chain_id == 10:
    data = data['op'] 
else:
    data = data['base']
pool_fac = interface.IPoolFactory(data['pool_factory'])
cl_fac = interface.ICLFactory(data['cl_pool_factory'])
voter = interface.IVoter(data['voter'])

LIMIT = 500

# Fetch all pools for a given token
def fetch(sugar, target):
    """
    Fetch all pools for a given token and return the data as a pandas DataFrame.

    Args:
        sugar (object): The LpSugar contract instance.
        target (str): The target token's address.

    Returns:
        pd.DataFrame: A DataFrame containing the pool information where the target token is present.
                      The DataFrame has columns ['pool', 'token_pos', 'is_cl'] and is indexed by 'pool'.
                      'token_pos' indicates the position of the token in the pool (0 or 1).
                      'is_cl' indicates if the pool is a concentrated liquidity pool (1) or not (0).
    """
    df = pd.DataFrame()
    columns = ['pool', 'token_pos', 'is_cl', 'fee_voting_reward', 'bribe_voting_reward', 'gauge', 'pool_created_blk', 'gauge_created_blk']
    df = pd.DataFrame(columns=columns)
    df = df.set_index('pool')
    
    results = [0] * LIMIT
    offset = 0
    while len(results) == LIMIT:
        results = sugar.all(LIMIT, offset)
        for res in results:
            pool, pool_type, token0, token1, fee_voting_reward, bribe_voting_reward, gauge = res[0], res[4], res[7], res[10], res[16], res[17], res[13]
            if token0 == target:
                df.at[pool, 'token_pos'] = 0
                df.at[pool, 'is_cl'] = 1 if pool_type > 0 else 0
                df.at[pool, 'fee_voting_reward'] = fee_voting_reward
                df.at[pool, 'bribe_voting_reward'] = bribe_voting_reward
                df.at[pool, 'gauge'] = gauge
            elif token1 == target:
                df.at[pool, 'token_pos'] = 1
                df.at[pool, 'is_cl'] = 1 if pool_type > 0 else 0
                df.at[pool, 'fee_voting_reward'] = fee_voting_reward
                df.at[pool, 'bribe_voting_reward'] = bribe_voting_reward
                df.at[pool, 'gauge'] = gauge
        offset += LIMIT

    non_cl_pools = df[df['is_cl'] == 0].index.to_list()
    results = pool_fac.events.PoolCreated.create_filter(fromBlock=0, argument_filters={'pool': non_cl_pools}).get_all_entries()
    for res in results:
        df.at[res.args.pool, 'pool_created_blk'] = res.blockNumber

    cl_pools = df[df['is_cl'] == 1].index.to_list()
    results = cl_fac.events.PoolCreated.create_filter(fromBlock=0, argument_filters={'pool': cl_pools}).get_all_entries()
    for res in results:
        df.at[res.args.pool, 'pool_created_blk'] = res.blockNumber

    results = voter.events.GaugeCreated.create_filter(fromBlock=0, argument_filters={'pool': df.index.tolist()}).get_all_entries()
    for res in results:
        df.at[res.args.pool, 'gauge_created_blk'] = res.blockNumber

    return df