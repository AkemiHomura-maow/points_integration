// SPDX-License-Identifier: MIT

interface IPool{
    function balanceOf(address user) external view returns(uint256 balance);
    function getReserves() external view returns (uint256 _reserve0, uint256 _reserve1, uint256 _blockTimestampLast);
    function totalSupply() external view returns (uint256 totalSupply);
}