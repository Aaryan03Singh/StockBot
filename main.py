import market as MK
import time


def start_the_trading(simulation,information):
    try:
        market = MK.Market(information,simulation)
        market.start()

        if simulation:
            while True:
                flag = market.get_ticks_for_simulation()
                if flag:
                    break
                # time.sleep()
        else:
            print("\nStopping bot...")
            market.stop()

    except KeyboardInterrupt:
        print("\nStopping bot...")
        market.stop()


SIMULATION = True

information = [
    {'stock_name':'IDEA','time_frame':'1minute','stratergy':'adx25','amount':1000},
    {'stock_name':'PCJEWELLER','time_frame':'1minute','stratergy':'adx25','amount':1000},
    {'stock_name':'IDEA','time_frame':'1minute','stratergy':'adx40','amount':1000},
]


if __name__ == "__main__":
    start_the_trading(simulation=SIMULATION,information=information)
    

