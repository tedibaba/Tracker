from webbrowser import get
from web3 import Web3
from collections import defaultdict
import csv
import requests
from dotenv import load_dotenv
import os

load_dotenv()
user_addr = os.getenv("USER_ADDRESS")
coin_mark_api = os.getenv("COIN_MARKET_API_KEY")
infura_api = os.getenv("INFURA_API_KEY")

min_abi = '''[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},
{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},
{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]'''

class Tracker():
    def __init__(self, user_addr):
        self.user_addr = user_addr
        self.infura_api = f"https://polygon-mainnet.infura.io/v3/{infura_api}"
        self.web3 = Web3(Web3.HTTPProvider(self.infura_api))
        self.contracts = defaultdict(lambda: None)
        
        self.get_tokens_from_csv('./token_addr.csv')
    
    def create_contract(self, token_addr):
        contract = self.web3.eth.contract(address=token_addr, abi=min_abi)
        self.contracts[token_addr] = [contract]
        self.contracts[token_addr].append(self.get_symbol(token_addr))

    def get_balance(self, token_addr):        
        balance = self.contracts[token_addr][0].functions.balanceOf(Web3.to_checksum_address(user_addr.lower())).call()
        decimals = self.contracts[token_addr][0].functions.decimals().call()
        return balance/(10**decimals)

    def get_symbol(self, token_addr):
        return self.contracts[token_addr][0].functions.symbol().call()

    def get_tokens_from_csv(self, csv_file):
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            tokens = []
            for row in csv_reader:
                tokens.append(row[0])
                self.create_contract(row[0])


    def convert_token_to_currency(self, symbol_list):
        headers = {"X-CMC_PRO_API_KEY": coin_mark_api}
        url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?symbol={','.join(symbol_list)}"
        response = requests.get(url, headers=headers)
        data = response.json()
        prices = []
        for symbol in symbol_list:
            prices.append(data['data'][symbol][0]['quote']['USD']['price'])
        return prices

def get_balances():
    tracker = Tracker(user_addr)
    token_list= [con[1] for con in tracker.contracts.values()]

    prices = tracker.convert_token_to_currency(token_list)
    total_value = 0
    token_value_dict = {}

    for i,token in enumerate(tracker.contracts.keys()):
        balance = tracker.get_balance(token)
        print(f"Token: {tracker.get_symbol(token)}")
        print(f"Balance: {balance}")
        print(f"USD Value: {prices[i] * balance}")
        print("")
        total_value += prices[i] * balance

    print(f"Total Value (USD): {total_value}")

def write_balances():
    pass

get_balances()