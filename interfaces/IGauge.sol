// SPDX-License-Identifier: MIT

interface IGauge{
    function balanceOf(address user) external view returns(uint256 balance);
}