import pandas as pd

LIMIT = 500

# Fetch all pools for a given token
def fetch(sugar, target):
    df = pd.DataFrame()
    columns = ['pool', 'token_pos', 'is_cl']
    df = pd.DataFrame(columns=columns)
    df = df.set_index('pool')
    
    results = [0] * LIMIT
    offset = 0
    while len(results) == LIMIT:
        results = sugar.all(LIMIT, offset)
        for res in results:
            pool, pool_type, token0, token1 = res[0], res[4], res[7], res[10]
            if token0 == target:
                df.at[pool, 'token_pos'] = 0
                df.at[pool, 'is_cl'] = 1 if pool_type > 0 else 0
            elif token1 == target:
                df.at[pool, 'token_pos'] = 1
                df.at[pool, 'is_cl'] = 1 if pool_type > 0 else 0
        offset += LIMIT
    return df