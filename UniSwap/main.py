"""
    Imports
"""
import requests
import json
import time
import func_triangular_arb


"""
    Uni V3 subgraph: https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v3
    Endpoint: https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3
    Get Graph QL mid prices for UNISWAP
"""
def retrieve_uniswap_info():
    query = """
        query {
        pools(
        orderBy: totalValueLockedETH,
        orderDirection: desc,
        first: 550) 
        {
            id
            totalValueLockedETH
            token0Price
            token1Price
            feeTier
            token0 {id symbol name decimals}
            token1 {id symbol name decimals}
        }}
    """
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    req = requests.post(url, json={"query": query})
    json_dict = json.loads(req.text)
    return json_dict


if __name__ ==  "__main__" :
    pairs = retrieve_uniswap_info()["data"]["pools"]
    structured_pairs = func_triangular_arb.struct_trading_pairs(pairs, limit=500)

    # Get surface rates
    surface_rate_list = []
    for t_pair in structured_pairs:
        surface_rate = func_triangular_arb.calc_triangular_arb_surface_rate(t_pair, min_rate=-0.1)
        if len(surface_rate) > 0:
            surface_rate_list.append(surface_rate)

    #Save to Json File
    if len(surface_rate_list) > 0:
        with open("uniswap_surface_rate.json", "w") as fp:
            json.dump(surface_rate_list, fp)
            print("File saved")





