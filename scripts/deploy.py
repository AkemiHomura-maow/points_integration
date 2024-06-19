from brownie import LpSugar, accounts, chain

acc = accounts.load('deployer')

if chain.id == 10:
    PoolLpSugar.deploy('0x41C914ee0c7E1A5edCD0295623e6dC557B5aBf3C', 
                    '0xF4c67CdEAaB8360370F41514d06e32CcD8aA1d7B', 
                    '0x416b433906b1B72FA758e166e239c43d68dC6F29',
                    '0x5Bd7E2221C2d59c99e6A9Cd18D80A5F4257D0f32',
                    {'from': acc})
    VotingRewardsHelper.deploy('0xFAf8FD17D9840595845582fCB047DF13f006787d', {'from':acc})
else:
    PoolLpSugar.deploy('0x16613524e02ad97eDfeF371bC883F2F5d6C480A5', 
                    '0x5C3F18F06CC09CA1910767A34a20F771039E37C0',
                    '0x827922686190790b37229fd06084350E74485b72',
                    '0x6d2D739bf37dFd93D804523c2dfA948EAf32f8E1',
                    {'from': acc})    
    VotingRewardsHelper.deploy('0xeBf418Fe2512e7E6bd9b87a8F0f294aCDC67e6B4',{'from':acc})

helper = VotingRewardsHelper.at('0x6fF159996Ec4237a9480E1B40857fa0c0F99C80c')

helper = VotingRewardsHelper.at('0x90D0368b5E96812568065bfebb43457282877743')
