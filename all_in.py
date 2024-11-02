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

def main():
    tick, status = get_tick()
    ticker_list = ['OWL','CROW','DOVE','DUCK']
    print("Trading has started.")

    yes = False

    while status == 'ACTIVE':
        for ticker_symbol in ticker_list:

            if get_order_status:
                s.post('http://localhost:'+port+'/v1/orders', params = {'ticker': ticker_symbol, 'type': 'MARKET', 'quantity': 5000, 'action': 'BUY'})
                yes = True

            sleep(0.75)
            s.post('http://localhost:'+port+'/v1/commands/cancel', params = {'ticker': ticker_symbol})

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

 
            
            
            





