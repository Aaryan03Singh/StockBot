from trader import Trader
from breeze_connect import BreezeConnect
from logger import get_logger
import breeze_config
import time
import pandas as pd
import simulator


class Market():

    def __init__(self,information,simulation=False):
        
        keys = {
            'api_key':breeze_config.API_KEY,
            'api_secret':breeze_config.API_SECRET,
            'session_token':breeze_config.SESSION_TOKEN
        }
        #directly take keys from breeze_config 
        self.breeze = BreezeConnect(api_key=keys['api_key'])
        self.breeze.generate_session(api_secret=keys['api_secret'],
                        session_token=keys['session_token'])
        
        self.logger = get_logger("MARKET")
        self.logger.info("Breeze object has been generated and authenticated")
        self.strategy_catalog = self.get_stocks_informarion(information)
        self.simulation = simulation
        
    def get_stock_names(self,stock_code):
        '''
         {'exchange_code': 'NSE',
        'exchange_stock_code': 'RELIANCE',
        'isec_stock_code': 'RELIND',
        'isec_token': '2885',
        'company name': 'RELIANCE INDUSTRIES',
        'isec_token_level1': '4.1!2885',
        'isec_token_level2': '4.2!2885'} 
        '''
        stock_names = self.breeze.get_names('NSE',stock_code)
        return stock_names
    
    def on_ticks(self,ticks):
        if 'last' in ticks:
            code = ticks['stock_name']
            purpose = 'price'
        else:
            code = f'{ticks['stock_code']}_{ticks['interval']}'
            purpose = 'ohlc'
        
        token = None
        interval = None
        stop_flag = 0
        for info in self.strategy_catalog[code]:
            token = info['isec_token_level1']
            interval = info['time_frame']
            if info['is_active']:
                flag = info['trader'].trade(ticks)
                stop_flag = stop_flag + flag
                if flag == 1:
                    info['is_active'] = False
       
        if stop_flag > 0:
            self.subscription_dict[code] = self.subscription_dict[code] - stop_flag
            if self.subscription_dict[code] == 0:
                if not self.simulation:
                    if purpose == 'ohlc':
                        self.unsubscribe(token,interval)
                    else:
                        self.unsubscribe(token)
                self.logger.info(f"The unsubscription has been made for {code} as no active traders are present")
  
    def get_stocks_informarion(self,information):
        info = {}
        for trade_info in information:
            temp_names = self.get_stock_names(trade_info['stock_code'])
            temp_information= {**temp_names,**trade_info}
            temp_information['is_active'] = False
            temp_information['trader'] = Trader(temp_information['stock_name'],temp_information['time_frame'],temp_information['stratergy'],temp_information['amount'])

            if self.simulation:
                temp_information['trader'].initialize_breeze_object(None)
            else:
                temp_information['trader'].initialize_breeze_object(self.breeze)
            
            ohlc_tick_flag = f'{temp_information['isec_stock_code']}_{temp_information['time_frame']}'
            price_tick_flag = f'{temp_information['company name']}'
            if ohlc_tick_flag in info:
                info[ohlc_tick_flag].append(temp_information)
            else:
                info[ohlc_tick_flag] = [temp_information]
            if price_tick_flag in info:
                info[price_tick_flag].append(temp_information)
            else:
                info[price_tick_flag] = [temp_information]

        return info
             
    def subscribe(self,stock_token,time_frame=None):
        if time_frame:
            self.breeze.subscribe_feeds(stock_token=stock_token, interval=time_frame)
        else:
            self.breeze.subscribe_feeds(stock_token=stock_token)

    def unsubscribe(self,stock_token,time_frame=None):
        if time_frame:
            self.breeze.unsubscribe_feeds(stock_token=stock_token, interval=time_frame)
        else:
            self.breeze.unsubscribe_feeds(stock_token=stock_token)

    def start(self):
        if self.simulation:
            self.subscription_dict , self.generator_dict = self.subscribtion_simulation()
        else:
            self.breeze.ws_connect()
            self.breeze.on_ticks = self.on_ticks
            self.subscription_dict = {}
            for code , information in self.strategy_catalog.items():
                if "_" in code:
                    purpose = 'ohlc'
                else:
                    purpose = 'price'

                for info in information:
                    if code in self.subscription_dict:
                        self.subscription_dict[code] = self.subscription_dict[code] + 1
                    else:
                        if purpose == 'ohlc':
                            self.subscribe(info['isec_token_level1'],info['time_frame'])
                        else:
                            self.subscribe(info['isec_token_level1'])
                        self.subscription_dict[code] = 1
                    
                    info['is_active'] = True
            #return the subscription dict and the list of generators if simulation

        self.logger.info(f"The subscriptions have been made - {self.subscription_dict}")

    def subscribtion_simulation(self):
        subscription_dict = {}
        generator_dict = {}
        for code , information in self.strategy_catalog.items():
            if "_" in code:
                purpose = 'ohlc'
            else:
                purpose = 'price'

            for info in information:
                if code in subscription_dict:
                    subscription_dict[code] = subscription_dict[code] + 1
                else:
                    if purpose == 'ohlc':
                        generator_dict[code] = simulator.simulation_generator(info,self.breeze)
                    subscription_dict[code] = 1
                
                info['is_active'] = True
        

        # self.logger.info(f"The subscriptions have been made - {self.subscription_dict}")
        return subscription_dict , generator_dict

    def stop(self):

        for code,information in self.strategy_catalog.items():
            if "_" in code:
                purpose = 'ohlc'    
            else:
                purpose = 'price'
            if self.subscription_dict[code] > 0:
                token = None
                interval = None
                for trader in information:
                    trader['is_active'] = False
                    token = trader['isec_token_level1']
                    interval = trader['time_frame']

                if purpose == 'ohlc':
                    self.unsubscribe(token,interval)
                else:
                    self.unsubscribe(token)
        
        self.breeze.ws_disconnect()
        
        self.logger.info("The unsubscriptions have been made for all the stocks")    

    def get_ticks_for_simulation(self):
        approved_ticks = {}
        for code , generator in self.generator_dict.items():
            candidate = next(generator)
            if 'last' in candidate:
                code  = candidate['stock_name']

            if self.subscription_dict[code] == 0:
                continue

            if code in approved_ticks:
                continue
            
            approved_ticks[code] = candidate

        for code, ticks in approved_ticks.items():
            self.on_ticks(ticks)





            

                

        





# information = [
#     {'stock_code':'IDEA','time_frame':'1minute','stratergy':'adx25','amount':1000},
#     {'stock_code':'PCJEWELLER','time_frame':'1minute','stratergy':'adx25','amount':1000}
# ]


# market = Market(keys,stocks_list,'adx25','1second',100)
# market.start()


# try:
#     print("Bot is running. Press Ctrl+C to stop.")
#     while True:
#         time.sleep(30)
# except KeyboardInterrupt:
#     print("\nStopping bot...")
#     # market.stop()
#     for stock in stocks_list:
#         market.stocks_info[stock]['trader'].data.to_csv(f"{stock}_data.csv",index=False)
# except Exception as e:
#     for stock in stocks_list:
#         market.stocks_info[stock]['trader'].data.to_csv(f"{stock}_data.csv",index=False)


