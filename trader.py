from calculator import Calculator
from stratergist import Stratergist
import pandas as pd
import math
import logger
import utils
from datetime import time as tt , date

class Trader():

    def __init__(self,stock,time_frame,stratergy,amount):

        self.logger = logger.get_logger(f"{stock}_{time_frame}_{stratergy}")  #add the name here 
        self.stock = stock
        self.time_frame = time_frame
        self.data = None
        self.calculator = Calculator()
        self.stratergist = Stratergist()
        self.stratergy = stratergy
        self.indicators , self.stoploss_percent , self.target_percent , self.number_of_candles= self.stratergist.initialize(stratergy,self.logger)
        self.trade_active = False
        self.latest_price = None
        self.price_data = None
        self.position_info = None
        self.amount = amount
        self.breeze = None
        self.number_of_trades = 0
        self.trading_done = False
        self.logger.info(f"Trader has started 🟢🚀")
    
    def initialize_breeze_object(self,breeze):
        self.breeze = breeze
        if breeze:
            self.logger.info(f"Currently in Prodcution mode with Breeze API connected 🔗")
        else:
            self.logger.info(f"Currently in Simulation mode 🛠️")
    
    def add_data(self,ohlc):
        ohlc = {k:v for k,v in ohlc.items() if k in ['open','high','low','close','volume','datetime']}
        ohlc['is_active'] = self.trade_active
        if self.data is None:
            temp_data = pd.DataFrame([ohlc])
        else:
            new = pd.DataFrame([ohlc])
            old = self.data
            temp_data = pd.concat([old,new])
            
        for required_indicator , indicator_information in self.indicators.items():
            indicator_type = list(indicator_information.keys())[0]
            temp_indicator = self.calculator.calculate(indicator_type,temp_data[['open','close','high','low','volume']].astype(float),indicator_information[indicator_type],self.logger)
            temp_data[required_indicator] = temp_indicator

        if temp_data.shape[1] != 7+ len(self.indicators):
            raise ValueError("The indicators were not caluclated properly")
        
        self.data = temp_data
        # self.logger.info(f"📊 OHLC received {ohlc}| Indicators calculated ⚙️ | Data shape: {self.data.shape}")
        self.logger.info(f"📊 OHLC received {ohlc}")
            
        return dict(self.data.iloc[-1])
    
    def update_price(self,price_data):
        price_data['is_active'] = self.trade_active
        if self.price_data is None:
            temp_price_data = pd.DataFrame([price_data])
        else:
            new = pd.DataFrame([price_data])
            old = self.price_data
            temp_price_data = pd.concat([old,new])

        self.price_data = temp_price_data        
        self.latest_price = {
            'time': price_data['time'],
            'price': float(price_data['price'])
        }
        return self.latest_price
        
    def next(self,data,purpose):
        if purpose == 'Enter':
            result = self.stratergist.enter_condition(self.stratergy,data,self.logger )
            return result
        elif purpose == 'Exit':
            result = self.stratergist.exit_condition(self.stratergy,data,self.logger)
            return result

    def enter(self,direction):
        stock_code = self.stock
        exchange_code = 'NSE'
        product = 'cash'
        order_type = 'market'
        if direction == 1:
            action = 'buy'
        else:
            action = 'sell'
        quantity = math.floor(self.amount / self.latest_price['price'])
        validity = 'day'

        if self.breeze:
            order_completion_details = self.breeze.place_order(stock_code=stock_code,
                        exchange_code=exchange_code,
                        product=product,
                        action=action,
                        order_type=order_type,
                        quantity=quantity,
                        validity=validity
                    )        
            order_id = order_completion_details['Success']['order_id']

            order_details= self.breeze.get_order_detail(exchange_code=exchange_code,order_id=order_id)
            # self.logger.info(order_details)
            price = float(order_details['Success'][0]['price']) #take the avg of the 'price'
        else:
            price = self.latest_price['price']
            order_id = 'simulated_order'

        if action == 'buy':
            stoploss = round(price * (1 - (self.stoploss_percent * 0.01)),2)
            target = round(price * (1 + (self.target_percent * 0.01)),2)
        else:
            stoploss = round(price * (1 + (self.stoploss_percent * 0.01)),2)
            target = round(price * (1 - (self.target_percent * 0.01)),2)

        position_data = {
            'stock_code' : stock_code,
            'exchange_code':exchange_code,
            'product':product,
            'action':action,
            'order_type':order_type,
            'quantity':quantity,
            'validity':validity,
            'enter_price':price,
            'order_id':order_id,
            'stoploss':stoploss,
            'target':target
        }

        self.logger.info(f"🟢🟢When have entered the position - {position_data}🟢🟢")

        return position_data

    def exit(self):
        if self.position_info['action'] == 'buy':
            action = 'sell'
        else:
            action = 'buy'
        
        if self.breeze:
            order_completion_details = self.breeze.place_order(stock_code=self.position_info['stock_code'],
                        exchange_code=self.position_info['exchange_code'],
                        product=self.position_info['product'],
                        action=action,
                        order_type=self.position_info['order_type'],
                        quantity=self.position_info['quantity'],
                        validity=self.position_info['validity']
                    )  
            
            order_id = order_completion_details['Success']['order_id']

            order_details= self.breeze.get_order_detail(exchange_code=self.position_info['exchange_code'],order_id=order_id)
            price = order_details['Success'][0]['average_price']
        else:
            price = self.latest_price['price']

        #add the logging over here
        self.logger.info(f"🔴🔴We have exited the position at price - {price}🔴🔴")
    
    def update_position(self):
        if self.position_info['action'] == 'buy':
            if self.latest_price['price'] >= self.position_info['target']:
                self.position_info['stoploss'] = self.position_info['target']
                self.position_info['target'] = round(self.position_info['target'] * (1.005),2)
                self.logger.info(f"The target was met we have changed the stop loss to  - {self.position_info['stoploss']} and target - {self.position_info['target']} 🎯🎯")
        else:
            if self.latest_price['price'] <= self.position_info['target']:
                self.position_info['stoploss'] = self.position_info['target']
                self.position_info['target'] = round(self.position_info['target'] * (0.995),2)
                self.logger.info(f"The target was met we have changed the stop loss to  - {self.position_info['stoploss']} and target - {self.position_info['target']} 🎯🎯")

    def trade(self,data):
        if 'last' in data:
            data_purpose = 'Exit'
            price  = data['last']
            time = data['ltt']
            price_info = self.update_price({'time':time,'price':price})
        else:
            data_purpose = 'Enter'
            ohlc_indicators = self.add_data(data)

        if not self.trading_done:
            if data_purpose == 'Enter' and not self.trade_active and utils.str_to_datetime_standard(ohlc_indicators['datetime']).time() <= tt(15, 14):
                if self.data.shape[0] >= self.number_of_candles:
                    data_to_send = []
                    for i in range(self.number_of_candles):
                        data_to_send.append(self.data.iloc[-(i+1)])
                    res = self.next(data_to_send,data_purpose)
                else:
                    res = 0
                if res == 1 or res == -1:
                    entry_data = self.enter(res)
                    self.trade_active = True
                    self.position_info = entry_data
                    # print(entry_data)
                
            elif data_purpose == 'Exit' and self.trade_active:
                self.update_position()
                res = self.next({**price_info,**self.position_info},data_purpose)
                if res == 1:
                    self.trade_active = False
                    self.exit()
                    self.position_info = None
                    self.number_of_trades = self.number_of_trades + 1
                else:
                    datetime_obj = utils.ltt_str_to_datetime(price_info['time']) 

                    cutoff = tt(15, 15) # 3:15 PM  (24-hour format)

                    if datetime_obj.time() >= cutoff:
                        self.trade_active = False
                        self.exit()
                        self.position_info = None
                        self.number_of_trades = self.number_of_trades + 1


            if self.number_of_trades >=1:
                self.trading_done = True


        #Saving the data when trading time for day is over 
        if data_purpose == 'Enter': 
            if utils.str_to_datetime_standard(ohlc_indicators['datetime']).time() >= tt(15, 15):
                self.data.to_csv(f"trading_diary/{str(date.today())}/data/{self.stock}_{self.time_frame}_{self.stratergy}_ohlc.csv",index=False)
        else:
            if utils.ltt_str_to_datetime(price_info['time']).time() >= tt(15, 15):
                self.price_data.to_csv(f"trading_diary/{str(date.today())}/data/{self.stock}_{self.time_frame}_{self.stratergy}_price.csv",index=False)

                
                
