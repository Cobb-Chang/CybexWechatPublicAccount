#!usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
import requests
import pandas as pd
import random
class MyCybex():
    def __init__(self):
        self.apilist = [
            'https://beijing.51nebula.com',
            'https://shanghai.51nebula.com'
            #'https://apihk.cybex.io'
        ]
        #调用
        self.AssetIDDic = {"1.3.27":"USDT",
                    "1.3.2":"ETH",
                    "1.3.3":"BTC",
                    "1.3.19":"MT",
                    "1.3.0":"CYB",
                    "1.3.24":"DPY",
                    "1.3.4":"EOS",
                    "1.3.654":"JCT",
                    "1.3.430":"MVP",
                    "1.3.26":"LTC",
                    "1.3.22":"KEY",
                    "1.3.28":"INK",
                    "1.3.5":"SNT",
                    "1.3.11":"PAY",
                    "1.3.23":"TCT",
                    "1.3.501":"NES"}
        self.AssetToID = {v:k for k,v in self.AssetIDDic.items()}
        self.AssetAccuracyDic = {"USDT":1000000,
                            "ETH":1000000,
                            "BTC":100000000,
                            "MT":1000000,
                            "DPY":1000000,
                            "EOS":1000000,
                            "JCT":1000000,
                            "CYB":100000,
                            "MVP":1000000,
                            "LTC":10000000,
                            "KEY":1000000,
                            "INK":1000000,
                            "SNT":1000000,
                            "PAY":1000000,
                            "TCT":1000000,
                            "NES":1000000}
    def call(self,method, params):
        data = {
        "jsonrpc":"2.0",
        "method":method, 
        "params":params,
        "id":1}
        jsondata = json.dumps(data)
        respone = requests.post(self.apilist[random.randint(0,len(self.apilist)-1)], data=jsondata)
        return json.loads(respone.text)
    #get block head
    def GetBlockHead(self,ID):
        return self.call('get_block_header',[ID])
    #根据账号ID获取名称
    def GetAccounts(self,ID):
        return self.call('get_accounts',[[ID]])
    ##根据ID，获取资产
    def GetAccountBalance(self,ID,*assetID):
        return self.call('get_account_balances',[ID,assetID])
    ##根据账户名，获取资产
    def GetAccountBalanceByName(self,Name,assetName):
        respone = self.call('get_named_account_balances',[Name,[self.AssetToID[assetName]]])
        if 'result' in respone.keys():
            result = int(respone['result'][0]['amount'])/int(self.AssetAccuracyDic[assetName])
        else:
            result = 'Error'
        return result