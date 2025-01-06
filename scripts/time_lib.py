def blk_to_ts(chain_id, blk):
    if chain_id == 10:
        return (blk - 120000000) * 2 + 1715598777
    elif chain_id == 8453:
        return (blk - 10000000) * 2 + 1706789347