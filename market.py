from trader import Trader
from breeze_connect import BreezeConnect
from logger import get_logger
import breeze_config
import time
import pandas as pd


keys = {
    'api_key':breeze_config.API_KEY,
    'api_secret':breeze_config.API_SECRET,
    'session_token':breeze_config.SESSION_TOKEN
}

market_logger = get_logger("market")

class Market():

    def __init__(self,keys,stock_codes,stratergy,time_frame,amount):
        self.breeze = BreezeConnect(api_key=keys['api_key'])
        self.breeze.generate_session(api_secret=keys['api_secret'],
                        session_token=keys['session_token'])
        market_logger.info("Breeze object has been generated and authenticated")
        self.time_frame = time_frame
        self.stratergy = stratergy
        self.amount = amount
        self.mapper ={}
        self.stocks_info = self.get_stocks_informarion(stock_codes)
        market_logger.info(f"The following values have been initialized for the market-\nTime frame -{self.time_frame}\nStratergy - {self.stratergy}\nAmount- {self.amount}\nStocks info -{self.stocks_info} ")
        

    def get_stock_token(self,stock_code):
        stock_names = self.breeze.get_names('NSE',stock_code)
        stock_code = stock_names['isec_stock_code']
        stock_token = stock_names['isec_token_level1']
        company_name = stock_names['company name']
        return stock_code , stock_token ,company_name
    
    def on_ticks(self,ticks):
        print("Ticks: {}".format(ticks))
        if 'last' in ticks:
            code = ticks['stock_name']
        else:
            code = ticks['stock_code']
        self.stocks_info[self.mapper[code]]['trader'].trade(ticks)


    def get_stocks_informarion(self,stock_codes):
        info = {}
        for stock in stock_codes:
            temp_information ={}
            temp_stock_code ,temp_stock_token ,temp_company_name =  self.get_stock_token(stock)
            temp_information['stock_token'] = temp_stock_token
            temp_information['stock_code'] = temp_stock_code
            temp_information['company_name'] = temp_company_name
            temp_information['trader'] = Trader(temp_stock_code,self.time_frame,self.stratergy,self.amount,get_logger(stock))
            temp_information['trader'].initialize_breeze_object(self.breeze)
            temp_information['is_active'] = False
            self.mapper[temp_stock_code] = stock
            self.mapper[temp_company_name] = stock
            info[stock] = temp_information

        return info
             
    def subscribe(self,stock_token):
        self.breeze.subscribe_feeds(stock_token=stock_token, interval=self.time_frame)

        self.breeze.subscribe_feeds(stock_token=stock_token)

    def unsubscribe(self,stock_token):

        self.breeze.unsubscribe_feeds(stock_token=stock_token, interval=self.time_frame)

        self.breeze.unsubscribe_feeds(stock_token=stock_token)

    
    def start(self):
        self.breeze.ws_connect()
        self.breeze.on_ticks = self.on_ticks
        for stock_code , information in self.stocks_info.items():
            self.subscribe(information['stock_token'])
            information['is_active'] = True
        print("The trading has started")

    def stop(self):
        for stock_code , information in self.stocks_info.items():
            self.unsubscribe(information['stock_token'])
            information['is_active'] = False
        self.breeze.ws_disconnect()
        print("The trading has stopped")


stocks_list = ['IDEA','PCJEWELLER','RTNPOWER','YESBANK','BCG']

market = Market(keys,stocks_list,'adx25','1minute',50)
market.start()


try:
    print("Bot is running. Press Ctrl+C to stop.")
    while True:
        time.sleep(30)
except KeyboardInterrupt:
    print("\nStopping bot...")
    # market.stop()
    for stock in stocks_list:
        market.stocks_info[stock]['trader'].data.to_csv(f"{stock}_data.csv",index=False)
except Exception as e:
    for stock in stocks_list:
        market.stocks_info[stock]['trader'].data.to_csv(f"{stock}_data.csv",index=False)


