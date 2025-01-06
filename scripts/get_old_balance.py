from brownie import interface

multicall = interface.IMulticall3('0xcA11bde05977b3631167028862bE2a173976CA11')
pools, gauges, gauge_created_blk = [], [], []

def set_vars(in_pools):
    global pools, gauges, gauge_created_blk
    pools, gauges, gauge_created_blk = in_pools.index.tolist(), in_pools['gauge'], in_pools['gauge_created_blk'].tolist()
    pools = [interface.IPool(pool) for pool in pools]
    gauges = [interface.IGauge(gauge) if gauge != '0x0000000000000000000000000000000000000000' else None for gauge in gauges]

def get_multicall_data(pool, gauge, users, blk):
    calls = []
    
    # Call getReserves and totalSupply once per pool
    calls.append((pool.address, pool.getReserves.encode_input()))
    calls.append((pool.address, pool.totalSupply.encode_input()))
    
    for user in users:
        calls.append((pool.address, pool.balanceOf.encode_input(user)))

        if blk > gauge_created_blk[pools.index(pool)]:
            calls.append((gauge.address, gauge.balanceOf.encode_input(user)))

    return calls

def get_old_balance(in_pools, users, blk):
    total_balances = {user: 0 for user in users}
    
    # Prepare the multicall data
    multicall_data = []
    for pool in in_pools:
        if pool in pools:
            i = pools.index(pool)
            multicall_data.extend(get_multicall_data(pools[i], gauges[i], users, blk))
    
    # Execute the multicall
    if multicall_data:
        responses = multicall.aggregate.call(multicall_data, block_identifier=blk)[1]

        k = 0
        last_i = -1
        # Process the responses
        for pool in in_pools:
            if pool in pools:
                i = pools.index(pool)
                # Determine base_index dynamically based on the block
                if last_i > -1 and blk > gauge_created_blk[last_i]:
                    base_index = k * (2 + 2 * len(users))  # 2 for reserves and total supply, 2 for each user
                else:
                    base_index = k * (2 + len(users))  # Only one balance call per user (unstaked)

                # Decode the reserves and total supply
                reserves = pools[i].getReserves.decode_output(responses[base_index])
                total_supply = pools[i].totalSupply.decode_output(responses[base_index + 1])
                reserve0, reserve1, _ = reserves  # Assuming getReserves returns (reserve0, reserve1)

                for j, user in enumerate(users):
                    user_index = j * (2 if blk > gauge_created_blk[i] else 1)  # 2 if staked balance is needed, else 1

                    # Decode the balances
                    unstaked = pools[i].balanceOf.decode_output(responses[base_index + 2 + user_index])
                    staked = gauges[i].balanceOf.decode_output(responses[base_index + 2 + user_index + 1]) if (blk > gauge_created_blk[i]) else 0

                    if total_supply > 0:
                        balance = int((unstaked + staked) / total_supply * reserve0)
                        total_balances[user] += balance
                k += 1
                last_i = i
    out_balances = [total_balances[usr] for usr in users]
    return out_balances