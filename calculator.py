import pandas_ta as ta 

class Calculator():

    def __init__(self):
        pass

    def calculate(self,indicator,data,indicator_data,logger):
        indicator = str.lower(indicator)
        method = getattr(self, f"calculate_{indicator}", None)
        if not method:
            raise NotImplementedError(f"{indicator} has not been included")
        
        try:
            result = method(data,indicator_data)
        except TypeError as e:
            logger.info(f"The error - {e} occured")
            result = None
        len = data.shape[0]
        if result is not None:
            return result
        else:
            return [None] * len

    def calculate_ma(self,data,indicator_data):
        result = ta.sma(close=data['close'],length=indicator_data['length'])
        return result
    
    def calculate_ema(self,data,indicator_data):
        result = ta.ema(close=data['close'],length=indicator_data['length'])
        return result
    
    def calculate_rsi(self,data,indicator_data):
        result = ta.rsi(close=data['close'],length=indicator_data['length'])
        return result
    
    def calculate_macd(self,data,indicator_data):
        temp = ta.macd(data["close"], fast=indicator_data['fast'], slow=indicator_data['slow'], signal=indicator_data['signal'])
        result = f'MACD_{indicator_data['fast']}_{indicator_data['slow']}_{indicator_data['signal']}'
        return temp[result]
    
    def calculate_histogram(self,data,indicator_data):
        temp = ta.macd(data["close"], fast=indicator_data['fast'], slow=indicator_data['slow'], signal=indicator_data['signal'])
        result = f'MACDh_{indicator_data['fast']}_{indicator_data['slow']}_{indicator_data['signal']}'
        return temp[result]
    
    def calculate_signal(self,data,indicator_data):
        temp = ta.macd(data["close"], fast=indicator_data['fast'], slow=indicator_data['slow'], signal=indicator_data['signal'])
        result = f'MACDs_{indicator_data['fast']}_{indicator_data['slow']}_{indicator_data['signal']}'
        return temp[result]
    
    def calculate_adx(self,data,indicator_data):
        temp = ta.adx(high=data["high"], low=data["low"], close=data["close"], length=indicator_data['length'])
        result = f'ADX_{indicator_data['length']}'
        return temp[result]


