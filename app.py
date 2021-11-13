from flask import Flask, session, render_template, flash
from flask_session import Session
from binance.client import Client
import config
import math
import itertools
import requests

app = Flask(__name__)
app.secret_key = b'kdrtfjd53453543jyrtjstjsrjstjhtsrhs'
client = Client(config.API_KEY, config.API_SECRET)
starting_crypto = "USDT"

@app.route('/')

def index():
    #############################################
    white_list = ["BNB", "EUR", "ETH"]
    fee = 0.075
    #############################################

    # Create stepSize.txt
    exchangeInfo = client.get_exchange_info()
    totalSymbols = exchangeInfo["symbols"]
    txt_file = open("stepSize.txt", "r+")
    txt_file.truncate(0)
    for symbol in totalSymbols:
        s0 = symbol
        st = symbol["symbol"]
        sz = symbol["filters"][2]["stepSize"]
        tt = st + ": " + sz
        txt_file.write(tt + "\n")
    txt_file.close()

    # Detect owned balances
    def owned():
        #############################################
        # Value in USDT to overcome for black listing
        greater = 5
        #############################################

        assets = client.get_exchange_info()
        symbol_assets = assets["symbols"]

        prices = client.get_all_tickers()

        account = client.get_account()
        balances = account["balances"]
        for balance in balances:
            if float(balance["free"]) > 0:
                
                global starting_crypto
                strAsset = str(balance["asset"]) + starting_crypto
                if strAsset in str(symbol_assets):
                    for price in prices:
                        if price["symbol"] == strAsset:
                            converted_price = float(price["price"]) * float(balance["free"])
                            if converted_price > greater:
                                yield balance["asset"]

                else:
                    strAsset = starting_crypto + str(balance["asset"])
                    if strAsset in str(symbol_assets):
                        for price in prices:
                            if price["symbol"] == strAsset:
                                converted_price = (1 / float(price["price"])) * float(balance["free"])
                                if converted_price > greater:
                                    yield balance["asset"]

    # Calculation quantities owned crypto 
    def raw_prices():
        assets = client.get_exchange_info()
        symbol_assets = assets["symbols"]
        prices = client.get_all_tickers()

        for blacked in black_list:
            global starting_crypto
            strAsset = str(blacked) + str(starting_crypto)
            if strAsset in str(symbol_assets):
                if blacked in str(client.get_symbol_info(strAsset)["baseAsset"]):
                    quantity = float(client.get_asset_balance(asset=blacked)["free"])
                    yield quantity
            else:
                strAsset = str(starting_crypto) + str(blacked)
                if strAsset in str(symbol_assets):
                    if blacked in str(client.get_symbol_info(strAsset)["quoteAsset"]):
                        for price in prices:
                            if price["symbol"] == strAsset:
                                quantity = (1 / float(price["price"])) * float(client.get_asset_balance(asset=blacked)["free"]) 
                                yield quantity

    # Function to calculate stepSize in number
    def stepSizer(sy):
        with open("stepSize.txt") as f:
            for num, line in enumerate(f, 1):
                if sy in line:
                    lineDect = line
                    lineDetected = lineDect.replace("\n", "")
                    stepSize_raw = lineDetected.partition(": ")[2]

                    stepSize_raw_position = stepSize_raw.find("1")
                    stepSize_pre_raw = stepSize_raw.partition(".")[2]
                    stepSize_pre_raw_raw = stepSize_pre_raw.partition("1")[0]
                    if stepSize_raw_position == 0:
                        noDec = True
                        return 0 
                    else:
                        noDec = False
                        return stepSize_pre_raw_raw.count("0") + 1
    
    # Truncate decimals without rounded them
    def truncate(f, n):
        return math.floor(f * 10 ** n) / 10 ** n

    # Detect black listed assets
    def symbols():
        assets = client.get_exchange_info()
        symbol_assets = assets["symbols"]
        prices = client.get_all_tickers()

        for blacked in black_list:
            global starting_crypto
            strAsset = str(blacked) + str(starting_crypto)
            if strAsset in str(symbol_assets):
                yield strAsset
            else:
                strAsset = str(starting_crypto) + str(blacked)
                if strAsset in str(symbol_assets):
                    yield strAsset

    ###########################################   

    owned = list(owned())
    black_list = [x for x in owned if x not in white_list]

    symbols = list(symbols())

    raw_prices = list(raw_prices())

    # Send orders
    def orders():
        for symbol, raw_price in zip(symbols, raw_prices):
            quantity = truncate(raw_price - ((raw_price * fee) / 100), stepSizer(symbol))
            if symbol.startswith(starting_crypto):
                side = "BUY"
            else:
                side = "SELL"
            try:
                client.create_order(symbol=symbol, side=side,type="MARKET",quantity=quantity)
                # print("\n" + str(symbol) + " ORDER DONE")
                yield symbol
            except Exception as e:
                flash(e.message, "error")
                # print("\n" + str(symbol) + " " + e.message)
                yield symbol
    
    orders = list(orders())

    return render_template("index.html", orders = orders)

if __name__ == '__main__':
  app.run(debug=True, host='127.0.0.1', port=80)
