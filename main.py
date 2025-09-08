import simulator
import trader
import time

information = {
    'stock': 'RELIANCE',
    'time_frame': '1minute',
    'company name': 'RELIANCE INDUSTRIES'
    }


rel_generator = simulator.simulation_generator(information)

t = trader.Trader(information['stock'],information['time_frame'],'adx25',10000)
t.initialize_breeze_object(None)

while True:
    tick = next(rel_generator)
    stop = t.trade(tick)
    if stop:
        break
    time.sleep(0.5)


