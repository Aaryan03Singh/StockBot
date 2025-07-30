from calculator import Calculator
from stratergist import Stratergist
import pandas as pd

class Trader():

    def __init__(self,stock,time_frame,stratergy,amount,logger):

        # if time_frame not in ['1min','5min']:
        #     raise ValueError('Time frame not valid, should be from the following values - ["1min","5min"]')
        
        #check is the stock code given is valid and store the value 
        self.stock = stock
        self.time_frame = time_frame
        self.data = None
        self.calculator = Calculator()
        self.stratergist = Stratergist(stratergy)
        self.stratergy = stratergy
        self.indicators , self.stoploss_percent , self.target_percent = self.stratergist.initialize()
        self.trade_active = False
        self.latest_price = None
        self.position_info = None
        self.amount = amount
        self.breeze = None
        self.logger = logger
        self.logger.info(f"The Trader has been setup with the following information -\nStock - {self.stock}\nTime Frame-{self.time_frame}\nStratergy - {self.stratergy}\nIndicators -{self.indicators}\nStopLoss Percent - {self.stoploss_percent}\nTarget Percent - {self.target_percent}\nAmount-{self.amount}")
        

    def __str__(self):
        stock_info = f"Stock being tracked is {self.stock}\n"
        time_frame_info = f"Timeframe being used is {self.time_frame}\n"
        return stock_info + time_frame_info
    
    def initialize_breeze_object(self,breeze):
        self.breeze = breeze
        self.logger.info(f"The breeze object inside has come - {self.breeze}")
    
    def add_data(self,ohlc):
        ohlc = {k:v for k,v in ohlc.items() if k in ['open','high','low','close','volume','datetime']}
        if self.data is None:
            temp_data = pd.DataFrame([ohlc])
        else:
            new = pd.DataFrame([ohlc])
            # old = self.data[['open','high','low','close','volume']]
            old = self.data
            temp_data = pd.concat([old,new])
        for required_indicator , indicator_information in self.indicators.items():
            indicator_type = list(indicator_information.keys())[0]
            temp_indicator = self.calculator.calculate(indicator_type,temp_data,indicator_information[indicator_type])
            temp_data[required_indicator] = temp_indicator

        if temp_data.shape[1] != 6+ len(self.indicators):
            raise ValueError("The indicators were not caluclated properly")
        
        self.data = temp_data
        self.logger.info(f"The OHLC data has been updated new shape of data - {self.data.shape}")
        if self.data.shape[0] == 1:
            self.logger.info(f"{self.data.iloc[0]}")
        
        return dict(self.data.iloc[-1])
    
    def update_price(self,price_data):
        self.latest_price = price_data
        self.logger.info(f"The latest price has been updated to {self.latest_price}")
        return self.latest_price
        
    def next(self,data,purpose):
        if purpose == 'Enter':
            result = self.stratergist.enter_condition(data)
            return result
        elif purpose == 'Exit':
            result = self.stratergist.exit_condition(data)
            return result

    def enter(self,direction):
        stock_code = self.stock
        exchange_code = 'NSE'
        product = 'margin'
        order_type = 'market'
        if direction == 1:
            action = 'buy'
        else:
            action = 'sell'
        quantity = round(self.amount / self.latest_price)
        validity = 'day'

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
        price = order_details['Success'][0]['average_price'] #take the avg of the 'price'

        if action == 'buy':
            stoploss = price * (1 - (self.stoploss_percent * 0.01))
            target = price * (1 + (self.target_percent * 0.01))
        else:
            stoploss = price * (1 + (self.stoploss_percent * 0.01))
            target = price * (1 - (self.target_percent * 0.01))

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

        print("When have entered the position")

        return position_data

    def exit(self):
        if self.position_info['action'] == 'buy':
            action = 'sell'
        else:
            action = 'buy'
        
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

        #add the logging over here
        
        print("We have exited the position")
    
    def update_position(self):
        if self.position_info['action'] == 'buy':
            if self.latest_price >= self.position_info['target']:
                self.position_info['stoploss'] = self.position_info['target']
                self.position_info['target'] = self.position_info['target'] * (1.005)
        else:
            if self.latest_price <= self.position_info['target']:
                self.position_info['stoploss'] = self.position_info['target']
                self.position_info['target'] = self.position_info['target'] * (0.995)
    

    def trade(self,data):
        if 'last' in data:
            self.logger.info("We have recieved price tick data")
            data_purpose = 'Exit'
            price  = data['last']
            time = data['ltt']
            price_info = self.update_price({'time':time,'price':price})
        else:
            self.logger.info("We have recieved OHLC data")
            data_purpose = 'Enter'
            ohlc_indicators = self.add_data(data)
            print(f"The ohlc data has been updated")


        if data_purpose == 'Enter' and not self.trade_active:
            res = self.next(ohlc_indicators,data_purpose)
            if res == 1 or res == -1:
                entry_data = self.enter(res)
                self.trade_active = True
                self.position_info = entry_data
                print(entry_data)
            
        elif data_purpose == 'Exit' and self.trade_active:
            self.update_position()
            res = self.next({**price_info,**self.position_info},data_purpose)
            if res == 1:
                self.trade_active = False
                self.exit()
                self.position_info = None
