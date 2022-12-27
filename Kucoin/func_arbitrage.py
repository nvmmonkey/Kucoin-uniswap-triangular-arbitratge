
import requests
import json
import time


# make a get requests
def get_coin_ticket(url):
    req = requests.get(url)
    json_response = json.loads(req.text)
    return json_response

#loop each objects to find the tradable pair
def struct_tradable(json_obj):
    coin_list = []
    for coin in json_obj:
        if coin["enableTrading"] == True: #finding enableTrading
            coin_list.append(coin["symbol"])
    return coin_list
def struct_all_pair(json_obj):
    coin_list = []
    for coin in json_obj:  #general finding
        coin_list.append(coin["symbol"])
    return coin_list

#structure tradable pairs
def struct_triangular_pairs(coin_list):
    triangular_pairs_list = []
    remove_duplicated_list = []
    pairs_list = coin_list[0:]

    # Get Pair A
    for pair_a in pairs_list:
        pair_a_split = pair_a.split("-")
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]

        # Assing A to a box
        a_pair_box = [a_base, a_quote]

    # Get Pair B
        for pair_b in pairs_list:
            pair_b_split = pair_b.split("-")
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]


            # Check Pair B
            if pair_b != pair_a:
                if b_base in a_pair_box or b_quote in a_pair_box:

                    # Get Pair C
                    for pair_c in pairs_list:
                        pair_c_split = pair_c.split("-")
                        c_base = pair_c_split[0]
                        c_quote = pair_c_split[1]


                        # count the number of matching C items
                        if pair_c != pair_a and pair_c != pair_b:
                            combine_all = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]


                            count_c_base = 0
                            for i in pair_box:
                                if i == c_base:
                                    count_c_base += 1


                            count_c_quote = 0
                            for i in pair_box:
                                if i == c_quote:
                                    count_c_quote += 1



                            # determining triangular match
                            if count_c_base == 2 and count_c_quote == 2:
                                combined = pair_a + "," + pair_b + "," + pair_c
                                unique_item = "".join(sorted(combine_all))
                                if unique_item not in remove_duplicated_list:
                                    match_dict = {
                                        "a_base": a_base,
                                        "b_base": b_base,
                                        "c_base": c_base,
                                        "a_quote": a_quote,
                                        "b_quote": b_quote,
                                        "c_quote": c_quote,
                                        "pair_a": pair_a,
                                        "pair_b": pair_b,
                                        "pair_c": pair_c,
                                        "combined": combined
                                    }
                                    triangular_pairs_list.append(match_dict)
                                    remove_duplicated_list.append(unique_item)
    return triangular_pairs_list

#Strutured prices
def get_price_for_t_pair (t_pair, price_json):

    #Extract Pair Inside
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    # Extract Prices infor for given Pair
    for pair in price_json:
        if pair["symbol"] == pair_a:
            pair_a_ask = float(pair['sell'])
            pair_a_bid = float(pair['buy'])
    for pair in price_json:
        if pair["symbol"] == pair_b:
            pair_b_ask = float(pair['sell'])
            pair_b_bid = float(pair['buy'])
    for pair in price_json:
        if pair["symbol"] == pair_c:
            pair_c_ask = float(pair['sell'])
            pair_c_bid = float(pair['buy'])

    # Output dictionary
    return {
        "pair_a_ask": pair_a_ask,
        "pair_a_bid": pair_a_bid,
        "pair_b_ask": pair_b_ask,
        "pair_b_bid": pair_b_bid,
        "pair_c_ask": pair_c_ask,
        "pair_c_bid": pair_c_bid
    }

    # pair_a_bid = price_json[pair_a]["buy"]
    # print(pair_a_ask, pair_a_bid)

# Calculated arbitrage surface rate for opportunities
def cal_triangular_arb_surface_rate(t_pair, price_dict):

    #Set variables
    starting_amount = 1
    min_surface_rate = 0
    surface_dict = {}
    contract_1 = ""
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquire_coin_t1 = 0
    acquire_coin_t2 = 0
    acquire_coin_t3 = 0
    calculated = 0

    #Extract Variables
    a_base = t_pair["a_base"]
    a_quote = t_pair["a_quote"]
    b_base = t_pair["b_base"]
    b_quote = t_pair["b_quote"]
    c_base = t_pair["c_base"]
    c_quote = t_pair["c_quote"]
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    # Extract Price Varible
    a_ask = price_dict["pair_a_ask"]
    a_bid = price_dict["pair_a_bid"]
    b_ask = price_dict["pair_b_ask"]
    b_bid = price_dict["pair_b_bid"]
    c_ask = price_dict["pair_c_ask"]
    c_bid = price_dict["pair_c_bid"]

    # Set directions and loops thru
    direction_list = ["forward", "reverse"]
    for direction in direction_list:

        #Set additional variables for swap information
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0

        """
            If swap from left(base) to right(quote), then * bid
            If swap from right(quote) to left(base), then * 1/ask
        """

        # Assume starting with a_base and swapping to a_quote
        if direction == "forward" and a_ask != 0 and a_bid != 0:
            swap_1 = a_base
            swap_2 = a_quote
            swap_1_rate = a_bid
            direction_trade_1 = "baseToQuote"
        if direction == "reverse" and a_ask != 0 and a_bid != 0:
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = 1/ a_ask
            direction_trade_1 = "quoteToBase"

        #Place the 1st trade
        contract_1 = pair_a
        acquire_coin_t1 = starting_amount * swap_1_rate




        """ FORWARD """
        # SCENE1: Check if a_quote(acquired coins) matches b_quote
        if direction == "forward" and b_ask != 0 and b_bid != 0:
            if a_quote == b_quote and calculated == 0:
                swap_2_rate = 1 / b_ask
                acquire_coin_t2 = acquire_coin_t1 * swap_2_rate #place 2nd trade
                direction_trade_2 = "quoteToBase"
                contract_2 = pair_b

                # If b_base (acquired coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = c_bid
                    direction_trade_3 = "baseToQuote"
                    contract_3 = pair_c

                # If b_base (acquired coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "quoteToBase"
                    contract_3 = pair_c

                # place 3rd trade
                acquire_coin_t3 = acquire_coin_t2 * swap_3_rate
                calculated = 1 #set calculated to True

        # SCENE2: Check if a_quote(acquired coins) matches b_base
        if direction == "forward" and b_ask != 0 and b_bid != 0:
            if a_quote == b_base and calculated == 0:
                swap_2_rate = b_bid
                acquire_coin_t2 = acquire_coin_t1 * swap_2_rate #place 2nd trade
                direction_trade_2 = "baseToQuote"
                contract_2 = pair_b

                # If b_quote (acquired coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = c_bid
                    direction_trade_3 = "baseToQuote"
                    contract_3 = pair_c

                # If b_quote (acquired coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = 1/ c_ask
                    direction_trade_3 = "quoteToBase"
                    contract_3 = pair_c

                # place 3rd trade
                acquire_coin_t3 = acquire_coin_t2 * swap_3_rate
                calculated = 1 #set calculated to True

        # SCENE3: Check if a_quote(acquired coins) matches c_quote
        if direction == "forward" and c_ask != 0 and c_bid != 0:
            if a_quote == c_quote and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquire_coin_t2 = acquire_coin_t1 * swap_2_rate #place 2nd trade
                direction_trade_2 = "quoteToBase"
                contract_2 = pair_c

                # If c_base (acquired coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = b_bid
                    direction_trade_3 = "baseToQuote"
                    contract_3 = pair_b

                # If c_base (acquired coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "quoteToBase"
                    contract_3 = pair_b

                # place 3rd trade
                acquire_coin_t3 = acquire_coin_t2 * swap_3_rate
                calculated = 1 #set calculated to True

        # SCENE4: Check if a_quote(acquired coins) matches c_base
        if direction == "forward" and c_ask != 0 and c_bid != 0:
            if a_quote == c_base and calculated == 0:
                swap_2_rate = c_bid
                acquire_coin_t2 = acquire_coin_t1 * swap_2_rate #place 2nd trade
                direction_trade_2 = "baseToQuote"
                contract_2 = pair_c

                # If c_quote (acquired coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = b_bid
                    direction_trade_3 = "baseToQuote"
                    contract_3 = pair_b

                # If c_quote (acquired coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = 1/ b_ask
                    direction_trade_3 = "quoteToBase"
                    contract_3 = pair_b

                # place 3rd trade
                acquire_coin_t3 = acquire_coin_t2 * swap_3_rate
                calculated = 1 #set calculated to True

        """ REVERSE """
        # SCENE1: Check if a_base(acquired coins) matches b_quote
        if direction == "reverse" and b_ask != 0 and b_bid != 0:
            if a_base == b_quote and calculated == 0:
                swap_2_rate = 1 / b_ask
                acquire_coin_t2 = acquire_coin_t1 * swap_2_rate  # place 2nd trade
                direction_trade_2 = "quoteToBase"
                contract_2 = pair_b

                # If b_base (acquired coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = c_bid
                    direction_trade_3 = "baseToQuote"
                    contract_3 = pair_c

                # If b_base (acquired coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "quoteToBase"
                    contract_3 = pair_c

                # place 3rd trade
                acquire_coin_t3 = acquire_coin_t2 * swap_3_rate
                calculated = 1  # set calculated to True

        # SCENE2: Check if a_base(acquired coins) matches b_base
        if direction == "reverse" and b_ask != 0 and b_bid != 0:
            if a_base == b_base and calculated == 0:
                swap_2_rate = b_bid
                acquire_coin_t2 = acquire_coin_t1 * swap_2_rate  # place 2nd trade
                direction_trade_2 = "baseToQuote"
                contract_2 = pair_b

                # If b_quote (acquired coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = c_bid
                    direction_trade_3 = "baseToQuote"
                    contract_3 = pair_c

                # If b_quote (acquired coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "quoteToBase"
                    contract_3 = pair_c

                # place 3rd trade
                acquire_coin_t3 = acquire_coin_t2 * swap_3_rate
                calculated = 1  # set calculated to True

        # SCENE3: Check if a_base(acquired coins) matches c_quote
        if direction == "reverse" and c_ask != 0 and c_bid != 0:
            if a_base == c_quote and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquire_coin_t2 = acquire_coin_t1 * swap_2_rate  # place 2nd trade
                direction_trade_2 = "quoteToBase"
                contract_2 = pair_c

                # If c_base (acquired coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = b_bid
                    direction_trade_3 = "baseToQuote"
                    contract_3 = pair_b

                # If c_base (acquired coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "quoteToBase"
                    contract_3 = pair_b

                # place 3rd trade
                acquire_coin_t3 = acquire_coin_t2 * swap_3_rate
                calculated = 1  # set calculated to True

        # SCENE4: Check if a_base(acquired coins) matches c_base
        if direction == "reverse" and c_ask != 0 and c_bid != 0:
            if a_base == c_base and calculated == 0:
                swap_2_rate = c_bid
                acquire_coin_t2 = acquire_coin_t1 * swap_2_rate  # place 2nd trade
                direction_trade_2 = "baseToQuote"
                contract_2 = pair_c

                # If c_quote (acquired coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = b_bid
                    direction_trade_3 = "baseToQuote"
                    contract_3 = pair_b

                # If c_quote (acquired coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "quoteToBase"
                    contract_3 = pair_b

                # place 3rd trade
                acquire_coin_t3 = acquire_coin_t2 * swap_3_rate
                calculated = 1  # set calculated to True

        """  PROFIT/LOSS OUTPUT """
        # Profit loss calculation
        profit_loss = acquire_coin_t3 - starting_amount
        profit_loss_perc = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

        # Trade description
        trade_description_1 = f"Start with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2} acquiring {acquire_coin_t1}."
        trade_description_2 = f"Swap {acquire_coin_t1} of {swap_2} at {swap_2_rate} for {swap_3} acquiring {acquire_coin_t2}."
        trade_description_3 = f"Swap {acquire_coin_t2} of {swap_3} at {swap_3_rate} for {swap_1} acquiring {acquire_coin_t3}."


        # Output Result
        if profit_loss_perc > min_surface_rate:
            surface_dict = {
                "swap_1": swap_1,
                "swap_2": swap_2,
                "swap_3": swap_3,
                "contract_1": contract_1,
                "contract_2": contract_2,
                "contract_3": contract_3,
                "direction_trade_1": direction_trade_1,
                "direction_trade_2": direction_trade_2,
                "direction_trade_3": direction_trade_3,
                "acquire_coin_t1": acquire_coin_t1,
                "acquire_coin_t2": acquire_coin_t2,
                "acquire_coin_t3": acquire_coin_t3,
                "swap_1_rate": swap_1_rate,
                "swap_2_rate": swap_2_rate,
                "swap_3_rate": swap_3_rate,
                "profit_loss": profit_loss,
                "profit_loss_perc": profit_loss_perc,
                "direction": direction,
                "trade_description_1": trade_description_1,
                "trade_description_2": trade_description_2,
                "trade_description_3": trade_description_3
            }
            return surface_dict

    return surface_dict

#Reformat orderbook for depth calculation
def reformated_orderbook(prices, contract_direction):
    price_list_main = []
    if contract_direction == "baseToQuote":
        for p in prices['bids']:
            bid_price = float(p[0])
            adj_price = bid_price if bid_price != 0 else 0
            adj_quantity = float(p[1])
            price_list_main.append([adj_price, adj_quantity])
    if contract_direction == "quoteToBase":
        for p in prices['asks']:
            ask_price = float(p[0])
            adj_price = 1 / ask_price if ask_price != 0 else 0
            adj_quantity = float(p[1]) * ask_price
            price_list_main.append([adj_price, adj_quantity])
    return price_list_main

#Get acquired coin AKA depth calculation
def calculated_acquired_coin(amount_in, orderbook):
    """
        Challenges:
        *Full amount of the available amount in can be eaten on the first level (level 0)
        **Some of the ammount in can be eaten by mmutilple levels
        ***Some coins may not have enough liquidity
    """
    #Initiatlise vairables
    trading_balance = amount_in
    quantity_bought = 0
    acquired_coin = 0
    counts = 0
    for level in orderbook:

        # Extract level price and quantity
        level_price = level[0]
        level_available_quantity = level[1]

        # Amount in is <= first level total amount
        if trading_balance <= level_available_quantity:
            quantity_bought = trading_balance
            trading_balance = 0
            amount_bought = quantity_bought * level_price
        # Amount in is > a given level total amount
        if trading_balance > level_available_quantity:
            quantity_bought = level_available_quantity
            trading_balance -= quantity_bought
            amount_bought = quantity_bought * level_price
        #Accumulated acquired coin
        acquired_coin = acquired_coin + amount_bought

        #EXIT TRADE
        if trading_balance == 0:
            return acquired_coin

        # EXIT if not enought orderbook levels
        counts += 1
        if counts == len(orderbook):
            return 0

#Get Depth from OrderBook
def get_depth_from_orderbook(surface_arb):

    # Extract initial variables
    swap_1 = surface_arb["swap_1"]
    starting_amount = 100
    starting_amount_dict = {
        "USDT" : 1000,
        "USDC" : 1000,
        "BTC" : 0.05,
        "ETH": 0.1
     }
    if swap_1 in starting_amount_dict:
        starting_amount = starting_amount_dict[swap_1]

    # Define pairs
    contract_1 = surface_arb["contract_1"]
    contract_2 = surface_arb["contract_2"]
    contract_3 = surface_arb["contract_3"]

    # Define direction for trade
    contract_1_direction = surface_arb["direction_trade_1"]
    contract_2_direction = surface_arb["direction_trade_2"]
    contract_3_direction = surface_arb["direction_trade_3"]

    #Get Orderbook depth for 1st 2nd 3rd trade
    url1 = f"https://api.kucoin.com/api/v1/market/orderbook/level2_20?symbol={contract_1}"
    depth_1_prices = get_coin_ticket(url1)['data']
    depth_1_reformatted_prices = reformated_orderbook(depth_1_prices, contract_1_direction)
    time.sleep(1)#api call limit

    url2 = f"https://api.kucoin.com/api/v1/market/orderbook/level2_20?symbol={contract_2}"
    depth_2_prices = get_coin_ticket(url2)['data']
    depth_2_reformatted_prices = reformated_orderbook(depth_2_prices, contract_2_direction)
    time.sleep(1)#api call limit

    url3 = f"https://api.kucoin.com/api/v1/market/orderbook/level2_20?symbol={contract_3}"
    depth_3_prices = get_coin_ticket(url3)['data']
    depth_3_reformatted_prices = reformated_orderbook(depth_3_prices, contract_3_direction)
    time.sleep(1)#api call limit


    # Get acquired coin
    acquired_coin_t1 = calculated_acquired_coin(starting_amount, depth_1_reformatted_prices)
    acquired_coin_t2 = calculated_acquired_coin(acquired_coin_t1, depth_2_reformatted_prices)
    acquired_coin_t3 = calculated_acquired_coin(acquired_coin_t2, depth_3_reformatted_prices)

    # Calculate profit loss AKA real rate
    profit_loss = acquired_coin_t3 - starting_amount
    real_rate_perc = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

    if real_rate_perc > -1:
        return_dict =  {
            "profit_loss": profit_loss,
            "real_rate_perc": real_rate_perc,
            "contract_1": contract_1,
            "contract_2": contract_2,
            "contract_3": contract_3,
            "contract_1_direction": contract_1_direction,
            "contract_2_direction": contract_2_direction,
            "contract_3_direction": contract_3_direction
        }
        return return_dict
    else:
        return {}