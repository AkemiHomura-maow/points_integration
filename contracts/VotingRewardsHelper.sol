// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IVotingEscrow{
    function ownerToNFTokenIdList(address _owner, uint256 _index) external view returns (uint256 _tokenId);
}

interface IReward{
    function earned(address token, uint256 tokenId) external view returns (uint256);
}

contract VotingRewardsHelper{
    IVotingEscrow public ve;

    constructor(address _ve){
        ve = IVotingEscrow(_ve);
    }

    function fetch(address _account, address _target, 
                   uint256 from, uint256 to,
                   IReward[] calldata _reward_contracts) public view returns (uint256 unclaimed, bool exhausted){

        for(uint i = from; i <= to; i++){
            uint256 id = ve.ownerToNFTokenIdList(_account, i);
            
            if (id == 0){
                exhausted = true;
                break;
            }
            
            for(uint j; j < _reward_contracts.length; j++){
                unclaimed += _reward_contracts[j].earned(_target, id);
            }
        }
        
    }
}