pragma solidity ^0.8.12;

/// @title Multicall3
/// @notice Aggregate results from multiple function calls
/// @dev Multicall & Multicall2 backwards-compatible
/// @dev Aggregate methods are marked `payable` to save 24 gas per call
/// @author Michael Elliot <mike@makerdao.com>
/// @author Joshua Levine <joshua@makerdao.com>
/// @author Nick Johnson <arachnid@notdot.net>
/// @author Andreas Bigger <andreas@nascent.xyz>
/// @author Matt Solomon <matt@mattsolomon.dev>
interface IMulticall3 {
    struct Call {
        address target;
        bytes callData;
    }

    function aggregate(Call[] calldata calls) external returns (uint256 blockNumber, bytes[] memory returnData);
}