import numpy as np
import pandas as pd
import utils

def _dirichlet_increments(total_change, k, rng, alpha=1.0):
    if k <= 0:
        return np.array([], dtype=float)
    mags = rng.dirichlet(np.full(k, alpha)) * abs(total_change)
    return np.sign(total_change) * mags

def simulate_path(
    start, low, high, end, n_steps, seed=None, order="any", smooth=1.0
):

    rng = np.random.default_rng(seed)

    # Decide order
    if order == "any":
        order = rng.choice(["low-first", "high-first"])
    if order not in ("low-first", "high-first"):
        raise ValueError("order must be 'any', 'low-first', or 'high-first'.")

    # Segment endpoints based on order
    if order == "low-first":
        waypoints = [start, low, high, end]
    else:  # "high-first"
        waypoints = [start, high, low, end]

    # Randomly allocate steps across 3 segments, each at least 1
    k1 = rng.integers(8, n_steps - 10)      # leave >=2 steps total for k2+k3
    k2 = rng.integers(8, n_steps - k1)     # leave >=1 step for k3
    k3 = n_steps - k1 - k2                  # guaranteed >=1

    ks = [k1, k2, k3]

    # Build increments for each segment so that we exactly hit each waypoint
    increments = []
    for seg_idx in range(3):
        a = waypoints[seg_idx]
        b = waypoints[seg_idx + 1]
        increments.append(_dirichlet_increments(b - a, ks[seg_idx], rng, alpha=smooth))

    increments = np.concatenate(increments)

    # Assemble the path
    path = np.empty(n_steps + 1, dtype=float)
    path[0] = waypoints[0]
    path[1:] = path[0] + np.cumsum(increments)
    return [float(round(p,2)) for p in path]

def get_data(isec_stock_code,breeze,interval):
    data= breeze.get_historical_data(interval=interval,
                    from_date= "2025-08-01T09:20:00.000Z",
                  to_date= "2025-08-30T09:22:00.000Z",
                   stock_code=isec_stock_code,
                   exchange_code="NSE",
                   product_type="cash")
    df = pd.DataFrame(data['Success'])
    df = df[pd.to_datetime(df['datetime']).dt.time >= pd.to_datetime("09:15").time()]
    return df

def simulation_generator(stock_information,breeze=None):

    # if  stock_information['stock'] == 'RELIANCE':
    #     df = pd.read_excel('rel.xlsx')
    #     df = df[pd.to_datetime(df['datetime']).dt.time >= pd.to_datetime("09:15").time()]
    # else:
    df = get_data(stock_information['isec_stock_code'],breeze,stock_information['time_frame'])
    stock_name = stock_information['company name']

    # df = df.astype({'low':'float','high':'float','open':'float','close':'float','volume':'int'})
    for _,row in df.iterrows():
        temp_ohlc_tick = {
                        'interval': stock_information['time_frame'],
                        'exchange_code': row['exchange_code'], 
                        'stock_code': row['stock_code'], 
                        'low': row['low'], 
                        'high': row['high'], 
                        'open': row['open'], 
                        'close': row['close'], 
                        'volume': row['volume'],
                        'datetime': row['datetime']
                        }
        yield temp_ohlc_tick
        timeframe_steps = {
            "1minute": 59,     # 60s - 1
            "5minute": 299,    # 5*60 - 1
            "15minute": 899,   # 15*60 - 1
            "30minute": 1799,  # 30*60 - 1
            "60minute": 3599   # 60*60 - 1
        }

        temp_prices_data = simulate_path(float(temp_ohlc_tick['open']),low=float(temp_ohlc_tick['low']), high=float(temp_ohlc_tick['high']), end=float(temp_ohlc_tick['close']),n_steps=timeframe_steps[stock_information['time_frame']])

        for price in temp_prices_data:
            yield {'symbol': '', #i sec token of the stock
            'open': '', #Opening price of the day
            'last': str(price), #Last traded price 
            'high': '', #Highest price of the day
            'low': '', #Lowest price of the day
            'change': '', #Change in percent from yesterdays close
            'bPrice': '', #Highest buy price bid
            'bQty': '', #Quantity of highest bid price 
            'sPrice': '', #Lowest Sell price 
            'sQty': '', #Quantity of lowest sell price
            'ltq': '', #Last traded quantity
            'avgPrice': '', #Average price of the day
            'quotes': '',
            'ttq': '', #Total quantity of the day (Volume)
            'totalBuyQt': '', #Buy Quantity 
            'totalSellQ': '', #Sell Quantity
            'ttv': '', #Total value traded in crores
            'trend': '', #Direction of the stock from open
            'lowerCktLm': '', #Lower Circuit amount 
            'upperCktLm': '', #Upper circuit amount
            'ltt': str(utils.datetime_to_ltt(utils.str_to_datetime_standard(temp_ohlc_tick['datetime']))),
            'close': '', #Yesterdays close price
            'exchange': 'NSE Equity',
            'stock_name': stock_name
            }

# info = {
#     'stock': 'RELIANCE',
#     'time_frame': '5minute',
#     'company name': 'RELIANCE INDUSTRIES',
#     'isec_stock_code': 'RELIND',
#     'stock_code': 'RELIANCE'
# }
# from breeze_connect import BreezeConnect
# import breeze_config
# keys = {
#     'api_key':breeze_config.API_KEY,
#     'api_secret':breeze_config.API_SECRET,
#     'session_token':breeze_config.SESSION_TOKEN
# }
# #directly take keys from breeze_config 
# breeze = BreezeConnect(api_key=keys['api_key'])
# breeze.generate_session(api_secret=keys['api_secret'],
#                 session_token=keys['session_token'])

# gen = simulation_generator(info,breeze)


# for i in range(320):
#     tick = next(gen)
#     print(tick)
    