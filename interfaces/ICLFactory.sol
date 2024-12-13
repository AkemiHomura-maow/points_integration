pragma solidity >=0.5.0;

interface ICLFactory {
    event PoolCreated(address indexed token0, address indexed token1, int24 indexed tickSpacing, address pool);
}