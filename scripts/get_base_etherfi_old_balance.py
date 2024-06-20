from brownie import interface
import concurrent.futures

pools = ['0x91f0f34916ca4e2cce120116774b0e4fa0cdcaa8', '0xc5adfb267a95df1233a2b5f7f48041e7fb384bca']
gauges = ['0xf8d47b641ed9df1c924c0f7a6deeea2803b9cfef', '0x0a5f63a1ac754b4418cc5381ee17e04ccad42f56']
pool_created_blk = [13614008, 14085276]
gauge_created_blk = [13655779, 14085500]

pools = [interface.IPool(pool) for pool in pools]
gauges = [interface.IGauge(gauge) for gauge in gauges]

def get_reserves(pool, blk):
    return pool.getReserves(block_identifier=blk)

def get_total_supply(pool, blk):
    return pool.totalSupply(block_identifier=blk)

def get_unstaked_balance(pool, user, blk):
    return pool.balanceOf(user, block_identifier=blk)

def get_staked_balance(gauge, user, blk):
    return gauge.balanceOf(user, block_identifier=blk)

def get_old_balance(user, blk):
    total_balance = 0
    futures = []
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i, pool in enumerate(pools):
            if blk > pool_created_blk[i]:
                futures.append((i, 'reserves', executor.submit(get_reserves, pool, blk)))
                futures.append((i, 'total_supply', executor.submit(get_total_supply, pool, blk)))
                futures.append((i, 'unstaked', executor.submit(get_unstaked_balance, pool, user, blk)))
                
                if blk > gauge_created_blk[i]:
                    futures.append((i, 'staked', executor.submit(get_staked_balance, gauges[i], user, blk)))
                else:
                    results.append((i, 'staked', 0))
        
        for i, key, future in futures:
            results.append((i, key, future.result()))
        
        # Organize results based on pool index and key
        organized_results = [{} for _ in range(len(pools))]
        for i, key, result in results:
            organized_results[i][key] = result
        
        for group in organized_results:
            if len(group) == 4:
                reserve0, reserve1, _ = group['reserves']
                total_supply = group['total_supply']
                unstaked = group['unstaked']
                staked = group['staked']
                
                balance = (unstaked + staked) / total_supply * reserve0
                total_balance += balance
    
    return total_balance

