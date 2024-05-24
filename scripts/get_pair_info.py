import pandas as pd

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
    columns = ['pool', 'token_pos', 'is_cl', 'fee_voting_reward', 'bribe_voting_reward']
    df = pd.DataFrame(columns=columns)
    df = df.set_index('pool')
    
    results = [0] * LIMIT
    offset = 0
    while len(results) == LIMIT:
        results = sugar.all(LIMIT, offset)
        for res in results:
            pool, pool_type, token0, token1, fee_voting_reward, bribe_voting_reward = res[0], res[4], res[7], res[10], res[16], res[17]
            if token0 == target:
                df.at[pool, 'token_pos'] = 0
                df.at[pool, 'is_cl'] = 1 if pool_type > 0 else 0
                df.at[pool, 'fee_voting_reward'] = fee_voting_reward
                df.at[pool, 'bribe_voting_reward'] = bribe_voting_reward
            elif token1 == target:
                df.at[pool, 'token_pos'] = 1
                df.at[pool, 'is_cl'] = 1 if pool_type > 0 else 0
                df.at[pool, 'fee_voting_reward'] = fee_voting_reward
                df.at[pool, 'bribe_voting_reward'] = bribe_voting_reward
        offset += LIMIT
    return df