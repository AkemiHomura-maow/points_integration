import requests
from io import StringIO
import pandas as pd
import json

data = json.load(open('./config.json'))

url = "https://drome.hyperdata.xyz/api/dataset/csv?format_rows=true"
headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "x-api-key": data['mb_key']
}

def v3_users_at_ts(pools, ts):
    pools = [pool.lower() for pool in pools]
    pools_str = "%2C+".join(pools)
    data = f"""query=%7B%22type%22%3A%22native%22%2C%22database%22%3A200%2C%22native%22%3A%7B%22template-tags%22%3A%7B%22pools%22%3A%7B%22type%22%3A%22text%22%2C%22name%22%3A%22pools%22%2C%22id%22%3A%2226bb3a10-cc7c-45e8-bfbf-fa512c959a6f%22%2C%22display-name%22%3A%22Pools%22%2C%22required%22%3Atrue%2C%22default%22%3A%220x6446021f4e396da3df4235c62537431372195d38%2C+0x7f770a81811b58094b75cea1de76304aa8eae72c%22%7D%7D%2C%22query%22%3A%22WITH+mints+AS%28%5Cn++++++++SELECT+DISTINCT+*%5Cn++++++++FROM%28%5Cn++++++++++++++++SELECT+tokenId%2C+t0.timestamp%2C+t1.to%2C+t0.transactionHash%5Cn++++++++++++++++FROM+public_CLPool_Mint+t0+INNER+JOIN+public_NFPM_Transfer+t1+ON+t0.transactionHash+%3D+t1.transactionHash%5Cn++++++++++++++++WHERE+chainId+%3D+8453+AND+%5C%22from%5C%22+%3D+%270x0000000000000000000000000000000000000000%27+AND+LOWER%28t0.sourceAddress%29+IN+%28SELECT+trim%28arrayJoin%28splitByString%28%27%2C%27%2C+%7B%7Bpools%7D%7D%29%29%29+%29%5Cn++++++++++++%29%5Cn++++%29%2C%5Cn++++burns+AS%28%5Cn++++++++SELECT+t_burn.tokenId%2C+t_burn.timestamp%2C+t_burn.%5C%22from%5C%22%2C+t_burn.transactionHash%5Cn++++++++FROM+public_NFPM_Transfer+t_burn+INNER+JOIN+mints+t_mints+ON+t_burn.chainId+%3D+8453+AND+t_burn.tokenId+%3D+t_mints.tokenId+AND+t_burn.to+%3D+%270x0000000000000000000000000000000000000000%27%5Cn++++%29%5Cn%5Cn%5CnSELECT+tokenId%2C+to+AS+user%2C+toUnixTimestamp%28timestamp%29+AS+ts%2C+True+AS+is_mint%5CnFROM+mints%5CnUNION+ALL%5CnSELECT+tokenId%2C+%5C%22from%5C%22%2C+toUnixTimestamp%28timestamp%29%2C+False%5CnFROM+burns%5Cn%22%7D%2C%22parameters%22%3A%5B%7B%22id%22%3A%2226bb3a10-cc7c-45e8-bfbf-fa512c959a6f%22%2C%22type%22%3A%22category%22%2C%22value%22%3A%22{pools_str}%22%2C%22target%22%3A%5B%22variable%22%2C%5B%22template-tag%22%2C%22pools%22%5D%5D%7D%5D%2C%22middleware%22%3A%7B%22js-int-to-string%3F%22%3Atrue%2C%22userland-query%3F%22%3Atrue%2C%22add-default-userland-constraints%3F%22%3Atrue%7D%7D&visualization_settings=%7B%22column_settings%22%3A%7B%7D%2C%22table.pivot%22%3Afalse%2C%22table.pivot_column%22%3A%22tokenId%22%2C%22table.cell_column%22%3A%22ts%22%2C%22table.columns%22%3A%5B%7B%22name%22%3A%22tokenId%22%2C%22enabled%22%3Atrue%7D%2C%7B%22name%22%3A%22user%22%2C%22enabled%22%3Atrue%7D%2C%7B%22name%22%3A%22ts%22%2C%22enabled%22%3Atrue%7D%2C%7B%22name%22%3A%22is_mint%22%2C%22enabled%22%3Atrue%7D%5D%2C%22table.column_formatting%22%3A%5B%5D%7D"""
    response = requests.post(url, headers=headers, data=data)
    response_io = StringIO(response.text)

    df = pd.read_csv(response_io)
    df['tokenId'] = df['tokenId'].str.replace(",", "").astype(int)
    df['ts'] = df['ts'].str.replace(",", "").astype(int)

    results = []
    for token_id, group in df.groupby('tokenId'):
        filtered_group = group[group['ts'] < ts]
        if (filtered_group['is_mint'] == True).any() and not (filtered_group['is_mint'] == False).any():
            results.append(group['user'].to_list()[0])
    return results