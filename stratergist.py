import numpy as np

class Stratergist():

    def __init__(self):
        pass
        # self.stratergy_name = stratergy_name

    def enter_condition(self,stratergy_name,data,logger):
        stratergy_name = str.lower(stratergy_name)
        method = getattr(self, f"{stratergy_name}_stratergy", None)
        if not method:
            raise NotImplementedError(f"{stratergy_name} has not been included")
        result = method(data,'enter',logger)
        return result

    def exit_condition(self,stratergy_name,data,logger):
        stratergy_name = str.lower(stratergy_name)
        method = getattr(self, f"{stratergy_name}_stratergy", None)
        if not method:
            raise NotImplementedError(f"{stratergy_name} has not been included")
        result = method(data,'exit',logger)
        return result

    def initialize(self,stratergy_name,logger):
        stratergy_name = str.lower(stratergy_name)
        method = getattr(self, f"{stratergy_name}_stratergy", None)
        if not method:
            raise NotImplementedError(f"{stratergy_name} has not been included")
        result = method("",'init',logger)
        return result

    def adx25_stratergy(self,data,usecase,logger):
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
        #add the time 
        stoploss_percentage = 0.3
        target_percentage = 0.3
        number_of_candles = 2
        if usecase == 'init':
            return parameters , stoploss_percentage , target_percentage, number_of_candles
        
        if usecase == 'enter':
            # 0 is nothing 1 to buy -1 to sell 
            # print(f"Data in the enter inside the strat - {data}")
            adx = data[0]['adx']
            # print(f"adx - {adx}  adx1 - {adx_2}")
            if adx is None or np.isnan(adx):
                logger.info(f"The adx right now is {adx} so not entering trade ⏳")
                return 0
            if adx > 10:
                logger.info(f"The adx right now is {adx} so ENTERING the trade")
                return 1
            else:
                logger.info(f"The adx right now is {adx} so not entering trade ⏳")
                return 0

            
        if usecase == 'exit':
            stoploss = data['stoploss']
            if data['action'] == 'buy':
                if data['price'] <= stoploss:
                    logger.info(f"The stoploss {stoploss} has been met 🛡️🛡️")
                    return 1
                else:
                    # logger.info("The stoploss has not been met")
                    return 0
            else:
                if data['price'] >= stoploss:
                    logger.info(f"The stoploss {stoploss} has been met 🛡️🛡️")
                    return 1
                else:
                    # logger.info("The stoploss has not been met")
                    return 0
                

    def adx40_stratergy(self,data,usecase,logger):
        parameters = {
           'adx':{'adx':{'length':7}},
        }
        #add the time 
        stoploss_percentage = 0.3
        target_percentage = 0.3
        number_of_candles = 2
        if usecase == 'init':
            return parameters , stoploss_percentage , target_percentage, number_of_candles
        
        if usecase == 'enter':
            # 0 is nothing 1 to buy -1 to sell 
            # print(f"Data in the enter inside the strat - {data}")
            adx = data[0]['adx']
            # print(f"adx - {adx}  adx1 - {adx_2}")
            if adx is None or np.isnan(adx):
                logger.info(f"The adx right now is {adx} so not entering trade ⏳")
                return 0
            if adx > 10:
                logger.info(f"The adx right now is {adx} so ENTERING the trade")
                return 1
            else:
                logger.info(f"The adx right now is {adx} so not entering trade ⏳")
                return 0

            
        if usecase == 'exit':
            stoploss = data['stoploss']
            if data['action'] == 'buy':
                if data['price'] <= stoploss:
                    logger.info(f"The stoploss {stoploss} has been met 🛡️🛡️")
                    return 1
                else:
                    # logger.info("The stoploss has not been met")
                    return 0
            else:
                if data['price'] >= stoploss:
                    logger.info(f"The stoploss {stoploss} has been met 🛡️🛡️")
                    return 1
                else:
                    # logger.info("The stoploss has not been met")
                    return 0
