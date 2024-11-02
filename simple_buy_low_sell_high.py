import requests
from collections import deque
from time import sleep

s = requests.Session()
s.headers.update({'X-API-key': 'API-KEY'})
port = "9988"

MAX_LONG_EXPOSURE = 300000
MAX_SHORT_EXPOSURE = -100000
ORDER_LIMIT = 5000

traded_prices = {ticker: None for ticker in ['OWL', 'CROW', 'DOVE', 'DUCK']}
def get_tick():
    resp = s.get('http://localhost:'+port+'/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick'], case['status']


def get_bid_ask(ticker):
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:'+port+'/v1/securities/book', params = payload)
    if resp.ok:
        book = resp.json()
        bid_side_book = book['bids']
        ask_side_book = book['asks']
        
        bid_prices_book = [item["price"] for item in bid_side_book]
        ask_prices_book = [item['price'] for item in ask_side_book]
        
        best_bid_price = bid_prices_book[0]
        best_ask_price = ask_prices_book[0]
  
        return best_bid_price, best_ask_price

def get_time_sales(ticker):
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:'+port+'/v1/securities/tas', params = payload)
    if resp.ok:
        book = resp.json()
        time_sales_book = [item["quantity"] for item in book]
        return time_sales_book

def get_position():
    resp = s.get ('http://localhost:'+port+'/v1/securities')
    if resp.ok:
        book = resp.json()
        return (book[0]['position']) + (book[1]['position']) + (book[2]['position'])

def get_open_orders(ticker):
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:'+port+'/v1/orders', params = payload)
    if resp.ok:
        orders = resp.json()
        buy_orders = [item for item in orders if item["action"] == "BUY"]
        sell_orders = [item for item in orders if item["action"] == "SELL"]
        return buy_orders, sell_orders

def get_order_status(order_id):
    resp = s.get ('http://localhost:'+port+'/v1/orders' + '/' + str(order_id))
    if resp.ok:
        order = resp.json()
        return order['status']

'''def main():
    tick, status = get_tick()
    ticker_list = ['OWL','CROW','DOVE','DUCK']
    print("Trading has started.")

    while status == 'ACTIVE':
        for ticker_symbol in ticker_list:
    
            position = get_position()
            best_bid_price, best_ask_price = get_bid_ask(ticker_symbol)
            
            last_price = traded_prices[ticker_symbol]
       
            if last_price and best_bid_price < last_price and position < MAX_LONG_EXPOSURE:
                s.post('http://localhost:'+port+'/v1/orders', params = {'ticker': ticker_symbol, 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_bid_price, 'action': 'BUY'})
                print(f"Buying {ticker_symbol} at {best_bid_price}")
                traded_prices[ticker_symbol] = best_bid_price
                
            elif last_price and best_bid_price > last_price and position > MAX_SHORT_EXPOSURE:
                s.post('http://localhost:'+port+'/v1/orders', params = {'ticker': ticker_symbol, 'type': 'LIMIT', 'quantity': ORDER_LIMIT, 'price': best_ask_price, 'action': 'SELL'})
                print(f"Selling {ticker_symbol} at {best_bid_price}")
                traded_prices[ticker_symbol] = best_ask_price
            
            if traded_prices[ticker_symbol] is None:
                traded_prices[ticker_symbol] = (best_bid_price + best_ask_price) / 2
            
            sleep(0.75)
            s.post('http://localhost:'+port+'/v1/commands/cancel', params = {'ticker': ticker_symbol})

        tick, status = get_tick()'''

def main():
    tick, status = get_tick()
    ticker = 'DOVE'  # Focus on DOVE for this strategy
    take_profit_margin = 0.02
    stop_loss_margin = 0.03  
    position = get_position()
    trade_size = 3000 

    while status == 'ACTIVE':
        best_bid_price, best_ask_price = get_bid_ask(ticker)
        
        # Calculate target buy/sell prices
        buy_price = best_bid_price * (1 - take_profit_margin)
        sell_price = best_ask_price * (1 + take_profit_margin)

        print(position)

        if position < MAX_LONG_EXPOSURE:
            # Place a limit buy order
            resp = s.post('http://localhost:9988/v1/orders', params={
                'ticker': ticker,
                'type': 'LIMIT',
                'quantity': trade_size,
                'price': buy_price,
                'action': 'BUY'
            })
            position += trade_size

        if position > MAX_SHORT_EXPOSURE:
            # Place a limit sell order
            resp = s.post('http://localhost:9988/v1/orders', params={
                'ticker': ticker,
                'type': 'LIMIT',
                'quantity': trade_size,
                'price': sell_price,
                'action': 'SELL'
            })
            position -= trade_size

        # STOP LOSS :)
        current_price = (best_bid_price + best_ask_price) / 2
        if position > 0 and current_price < best_bid_price * (1 - stop_loss_margin):
            
            s.post('http://localhost:9988/v1/orders', params={
                'ticker': ticker,
                'type': 'MARKET',
                'quantity': position,
                'price': current_price,
                'action': 'SELL'
            })
            position = 0  # Reset position
        
        sleep(1.5)
        tick, status = get_tick()



if __name__ == '__main__':
    count = 0
    mode = int(input("Enter 1 for Debugging Mode and 0 for Testing Mode \n Your Response: "))
    
    if mode == 1:
        main()
    else:
        while True:
            try:
                main()
            except:
                pd = count % 3 + 1
                print("waiting" + "." * pd)
                count += 1

 
            
            
            





