pragma solidity >=0.5.0;

interface IPoolFactory {
    event PoolCreated(address indexed token0, address indexed token1, bool indexed stable, address pool, uint256);
}