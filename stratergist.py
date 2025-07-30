class Stratergist():

    def __init__(self,stratergy_name):
        self.stratergy_name = stratergy_name

    def enter_condition(self,data):
        stratergy_name = str.lower(self.stratergy_name)
        method = getattr(self, f"{stratergy_name}_stratergy", None)
        if not method:
            raise NotImplementedError(f"{stratergy_name} has not been included")
        result = method(data,'enter')
        return result

    def exit_condition(self,data):
        stratergy_name = str.lower(self.stratergy_name)
        method = getattr(self, f"{stratergy_name}_stratergy", None)
        if not method:
            raise NotImplementedError(f"{stratergy_name} has not been included")
        result = method(data,'exit')
        return result

    def initialize(self):
        stratergy_name = str.lower(self.stratergy_name)
        method = getattr(self, f"{stratergy_name}_stratergy", None)
        if not method:
            raise NotImplementedError(f"{stratergy_name} has not been included")
        result = method("",'init')
        return result

    def adx25_stratergy(self,data,usecase):
        parameters = {
           'adx':{'adx':{'length':7}},
           'ema6':{'ema':{'length':6}},
           'ema12':{'ema':{'length':12}},
           'ma':{'ma':{'length':12}},
           'rsi':{'rsi':{'length':12}},
           'macd':{'macd':{'fast':6,'slow':12,'signal':7}},
           'signal':{'signal':{'fast':6,'slow':12,'signal':7}},
           'histogram':{'histogram':{'fast':6,'slow':12,'signal':7}}
        }
        stoploss_percentage = 1
        target_percentage = 1
        if usecase == 'init':
            return parameters , stoploss_percentage , target_percentage
        
        if usecase == 'enter':
            # 0 is nothing 1 to buy -1 to sell 
            adx = data['adx']
            if adx is None:
                return 0
            if adx >= 10000:
                return 1
            else:
                return 0
            
        if usecase == 'exit':
            stoploss = data['stoploss']
            if data['action'] == 'buy':
                if data['price'] <= stoploss:
                    return 1
                else:
                    return 0
            else:
                if data['price'] >= stoploss:
                    return 1
                else:
                    return 0
