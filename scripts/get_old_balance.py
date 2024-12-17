from brownie import interface,chain

if chain.id != 10:
    pools = ['0x91f0f34916ca4e2cce120116774b0e4fa0cdcaa8', '0xc5adfb267a95df1233a2b5f7f48041e7fb384bca']
    gauges = ['0xf8d47b641ed9df1c924c0f7a6deeea2803b9cfef', '0x0a5f63a1ac754b4418cc5381ee17e04ccad42f56']
    gauge_created_blk = [13655779, 14085500]
else:
    pools = ['0xe48b4e392e4fc29ac2600c3c8efe0404a15d60d9', '0x5b70eb1d273da41c40316bf7d3baf7fdfae6abd2', '0xd0F92F5d756Bf223574DFa3ef284a35C3c046289']
    gauges = ['0x0b5f85ed904a06efdb893510cca20481a5de4965', '0xBc5A46217b96946C6A57c5D0134980FFA2541CC5', '0xb41d2e680bedfa618179b5fe9cd07dcdcf7a4a36']
    gauge_created_blk = [119165909, 124981694,121498676]

multicall = interface.IMulticall3('0xcA11bde05977b3631167028862bE2a173976CA11')

pools = [interface.IPool(pool) for pool in pools]
gauges = [interface.IGauge(gauge) for gauge in gauges]

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
        # Process the responses
        for pool in in_pools:
            if pool in pools:
                i = pools.index(pool)
                # Determine base_index dynamically based on the block
                if blk > gauge_created_blk[i]:
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
    out_balances = [total_balances[usr] for usr in users]
    return out_balances