import json
import time
import func_arbitrage

#Set Variable
coin_price_url = "https://api.kucoin.com/api/v1/market/allTickers"

# STEP0: Gather Correct Coins
'''
    STEP0: find coins to truad
    Exchange: Kucoin
    API Docs: https://docs.kucoin.com/#base-url
    API Socket: https://api.kucoin.com
'''

def step_0():
# Extract list of coins/price on Kucoin
    coin_json = func_arbitrage.get_coin_ticket(coin_price_url)["data"]["ticker"]
    coin_enable_json = func_arbitrage.get_coin_ticket("https://api.kucoin.com/api/v2/symbols")['data']
    # polon_json = func_arbitrage.get_coin_ticket("https://api.poloniex.com/markets")


    # Loop each object and find traderable pairs
    coin_tradable_list = func_arbitrage.struct_tradable(coin_enable_json)
    coin_list = func_arbitrage.struct_all_pair(coin_json)
    # polonix_coin_list = func_arbitrage.struct_all_pair(polonix_coin_json)

    # print(coin_tradable_list)
    # print(coin_list)

    # print("Length of enable_list is", len(coin_tradable_list))
    # print("Length of tradable list (enableTrading method) is", len(coin_enable_json))
    # print("Length of live priced trading pairs is", len(coin_list))

    # return list of tradable coins
    return coin_list


# STEP1: Gather Correct Coins
'''
    STEP1: Structuring Triangular Pairs
    Calculation Only
'''

def step_1(coin_list):
    # structured list of trableable triangular arbitrage pairs
    structured_list = func_arbitrage.struct_triangular_pairs(coin_list)

    #save structured list
    with open("structured_list.json","w") as fp:
        json.dump(structured_list, fp)

#STEP2: Calculate Arbitrage opportunities surface rate
'''
    Exchange: Kucoin
    API Docs: https://docs.kucoin.com/#base-url
    API Socket: https://api.kucoin.com
'''
def step_2():
    #Get structured pairs
    with open("structured_list.json") as json_file:
        strutured_pairs = json.load(json_file)

    #Get latest surface prices
    price_json = func_arbitrage.get_coin_ticket(coin_price_url)["data"]["ticker"]

    # Loop through and get structured pairs' price information
    for t_pair in strutured_pairs:
        time.sleep(0.3)
        price_dict = func_arbitrage.get_price_for_t_pair(t_pair, price_json)
        surface_arb = func_arbitrage.cal_triangular_arb_surface_rate(t_pair, price_dict)

        if len(surface_arb) > 0:
            real_rate_arb = func_arbitrage.get_depth_from_orderbook(surface_arb)
            print(real_rate_arb)
            time.sleep(15)


'''Main Section'''
if __name__ == "__main__":
    # coin_tradable_list = step_0()
    # structured_pair = step_1(coin_tradable_list)
    while True:
        step_2()


