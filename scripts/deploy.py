from brownie import LpSugar, accounts, chain

acc = accounts.load('deployer')

if chain.id == 10:
    PoolLpSugar.deploy('0x41C914ee0c7E1A5edCD0295623e6dC557B5aBf3C', 
                    '0xF4c67CdEAaB8360370F41514d06e32CcD8aA1d7B', 
                    '0xbB5DFE1380333CEE4c2EeBd7202c80dE2256AdF4',
                    '0x5Bd7E2221C2d59c99e6A9Cd18D80A5F4257D0f32',
                    {'from': acc})
else:
    PoolLpSugar.deploy('0x16613524e02ad97eDfeF371bC883F2F5d6C480A5', 
                    '0x5C3F18F06CC09CA1910767A34a20F771039E37C0',
                    '0xc741beb2156827704A1466575ccA1cBf726a1178',
                    '0x6d2D739bf37dFd93D804523c2dfA948EAf32f8E1',
                    {'from': acc})    
