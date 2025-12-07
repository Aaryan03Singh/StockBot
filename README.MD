FLOW OF THE BOT-

**Set up the breeze_config.py**
Register an app in icici breeze and then in the breeze_config.py file set the following details
API_KEY 
API_SECRET 
SESSION_TOKEN 

Have to check and generate new session_token everyday 

**Initialize market**

Initialize the market with the following parameters
Information Dictionary -
In the following format 
information = [
    {'stock_name':'IDEA','time_frame':'1minute','stratergy':'adx25','amount':1000},
    {'stock_name':'PCJEWELLER','time_frame':'1minute','stratergy':'adx25','amount':1000},
    {'stock_name':'IDEA','time_frame':'1minute','stratergy':'adx40','amount':1000},
]

Ensure that the time_frame is the same across the stocks and stratergies are supported by the bot

Simulation or Live Market


On initialization first the logger is set up and the breeze object of the market is created. 

Then the stratergy catalog for the market is made 

For each stock info the following details are added - 
{
    **Info gave in initialization 
    ** All the different names of the stock 
    {'exchange_code': 'NSE',
        'exchange_stock_code': 'RELIANCE',
        'isec_stock_code': 'RELIND',
        'isec_token': '2885',
        'company name': 'RELIANCE INDUSTRIES',
        'isec_token_level1': '4.1!2885',
        'isec_token_level2': '4.2!2885'} 
    is_active : True/False
    the individual traders for each stratergy are set 
    Each trader is given access to the markets breeze object (But in case of simulation the Trader is given None)
}

With the information the Stratergy Catalog is made in the following format- 

{
    for ohlc data - "isec_stock_code_time_frame" : [list of information dict that use that ohlc data ],
    for tick data - "company_name" : [list of information dict that use that tick data ]
}

The information dicts can be in both ohlc and tick data lists 

**Start the Market**

In case for not simulations-
breeze object is connected to web socket and data starts flowing in
the on_ticks is set to on ticks function of the market object

The subscription_dict if made and for simulation the generator_dict is made

Subscription dict is in the following format (similar to the stratergy catalog but instead of list of information dicts it has the number of active users for that data) -

{
    'ohlc': number of traders using the data,
    'tick': number of traders using the data
}


Also while creating the subsciption dict the is_active is set to True for each information in the startergy catalog

For simulation the generator dict is made in the following format -

{
    'ohlc': generator function for ohlc data
}

In this case only ohlc data is there beacuse the tick data is also generated from the same generator 


**On Ticks Functionality**

Based on the tick it sees makes the code and then from startergy catalog gets the list of information dicts that use that data

Send the tick to each trader object in the information dict

If the traders sends stop flag as 1 it sets that specific trader to inactive (is_active = False)
and then recreates the subscription dict to reflect the changes

If any subscription in the subscription dict goes to zero it disconnects from that data stream

Note - 
The ws connection is subscribed and unsubscribed using 'isec_token_level1'
But tick data gives - 'company_name'
Ohlc data give - 'isec_stock_code'


**Trader Object Functionality**

On initilization the trader object- 
Requires the info - 
{
    Stock Name,
    Time Frame,
    Stratergy,
    Amount
}

From this it initializes the Calculator and Strategist then gets the stoploss , target , number of candles 

When ever a tick comes it updates the ohlc data and the tick data 

Checks the conditions for entry and exit buys / sells / updates stoploss 

Finally when position is exited it sends the stop flag  

**Generator Get Ticks**

Goes through all the generators - 
Gets tick checks if the subscription dict has any active users for that data  if not ignores tick
Checks if the same tick has already come if yes then ignores the tick 

Sends the tick to the on_ticks function of the market object

If all ticks are ignored means no more ticks so sends the signal to stop getting more ticks 


















