#!usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
import threading
import websocket
import requests
from datetime import datetime, timedelta, timezone
import pandas as pd
import random
from NewsPost import *
MAX_TRIES = 3
apilist = [
    'https://beijing.51nebula.com',
    'https://shanghai.51nebula.com'
    #'https://apihk.cybex.io'
]
#调用
AssetIDDic = {"1.3.27":"USDT",
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
              "1.3.23":"TCT"}
AssetAccuracyDic = {"USDT":1000000,
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
                    "TCT":1000000}
def call(method, params):
    data = {
    "jsonrpc":"2.0",
    "method":method, 
    "params":params,
    "id":1}
    jsondata = json.dumps(data)
    respone = requests.post(apilist[random.randint(0,len(apilist)-1)], data=jsondata)
    return json.loads(respone.text)
#get block head
def GetBlockHead(ID):
    return call('get_block_header',[ID])
#根据账号ID获取名称
def GetAccounts(ID):
    return call('get_accounts',[[ID]])
##根据ID，获取资产
def GetAccountBalance(ID,*assetID):
    return call('get_account_balances',[ID,assetID])

def run_in_thread(sec):
    def _wrapper(func):
        def __wrapper(self, *args, **kwargs):
            timer = threading.Timer(sec, func, [self, *args])
            timer.start()
            tries = 0
            while True:
                try:
                    self._ws.on_open = self.on_open
                    self._ws.run_forever()
                    break
                except:
                    if tries > MAX_TRIES:
                        raise
                    else:
                        self.reset()
                        tries += 1
                        time.sleep(2)
            return self._result
        return __wrapper
    return _wrapper

class CybexHistoryAPI(object):
    def __init__(self, ws_endp):
        self._endpoint = ws_endp
        self.reset()

    def reset(self):
        self._ws = websocket.WebSocketApp(self._endpoint,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close)
        self._login_api_id = -1
        self._history_api_id = -1
        self._api_is_ready = False
        self._call_id = 1

    def _send_msg(self, params):
        call = {"id": self._call_id, "method": "call",
                "params": params}
        self._ws.send(json.dumps(call))
        self._call_id += 1

    def on_open(self):
        self._send_msg([1, "login", ["",""]])
        self._call_id = 1

    def on_error(self,error):
        print('Remote node send an error [{}]'.format(error))

    def on_close(self):
        print('Remote node closed our connection')

    def on_message(self,msg):
        if self._login_api_id < 0:
            result = json.loads(msg)
            self._login_api_id = result['id']
            self._send_msg([self._login_api_id, "history", []])
        elif self._history_api_id < 0:
            result = json.loads(msg)
            self._history_api_id = result['result']
            self._api_is_ready = True
        else:
            self._result = json.loads(msg)['result']
            self._ws.close()
            self.reset()

    @run_in_thread(0.01)
    def get_account_history(self, account_id, stop, limit, start):
        while not self._api_is_ready:
            time.sleep(0.01)
        self._send_msg([self._history_api_id, "get_account_history",
            [account_id, stop, limit, start]])

    @run_in_thread(0.01)
    def get_market_history(self, base_id, quote_id, ts, start, end):
        while not self._api_is_ready:
            time.sleep(0.01)
        self._send_msg([self._history_api_id, "get_market_history",
            [base_id, quote_id, ts, start, end]])

    @run_in_thread(0.01)
    def get_fill_order_history(self, base_id, quote_id, limit):
        while not self._api_is_ready:
            time.sleep(0.01)
        self._send_msg([self._history_api_id, "get_fill_order_history",
            [base_id, quote_id, limit]])
        
def scan_account(acc_id, max_len = 100):
    api = CybexHistoryAPI('wss://shanghai.51nebula.com/')
    start = 0
    tot_len = 0
    result = []
    while tot_len < max_len:
        ret = api.get_account_history(acc_id, '1.11.1', 100, '1.11.' + str(start))
        if len(ret) == 0 or int(ret[0]['id'].split('.')[-1]) == start:
            break
        tot_len += len(ret)
        start = int(ret[-1]['id'].split('.')[-1]) - 1
        result.extend(ret)

    return result

def updateTransferRecord(respone,LatestBlockID):

    for items in respone[::-1]:
        if items['op'][0]==0:
            if items['block_num'] > LatestBlockID:

                BlockNum = items['block_num']
                timestamprespone = GetBlockHead(str(BlockNum))['result']['timestamp']
                blocktime = timestamprespone.split('T')
                HourCalcul_temp = blocktime[1].split(':')
                if int(HourCalcul_temp[0])>=16:
                    hourtemp = int(HourCalcul_temp[0])-16
                else:
                    hourtemp = int(HourCalcul_temp[0])+8
                blocktime[1] = str(hourtemp)+':'+HourCalcul_temp[1]+':'+HourCalcul_temp[2] 
                AssetID = items['op'][1]['amount']['asset_id']
                if AssetID in AssetIDDic:
                    AssetName = AssetIDDic[AssetID]
                    Amount = int(items['op'][1]['amount']['amount'])/AssetAccuracyDic[AssetIDDic[AssetID]]
                else:
                    AssetName = AssetID
                    Amount = items['op'][1]['amount']['amount']
                FromAccount = GetAccounts(items['op'][1]['from'])['result'][0]['name']
                ToAccount = GetAccounts(items['op'][1]['to'])['result'][0]['name']
                #pubilc
                #respone = requests.get("https://pushbear.ftqq.com/sub?sendkey=6381-e0f8a7d666a4ed157ad592d8c5708351&text={}&desp={}".format(AssetName,FromAccount+'在'+blocktime[1]+'转给'+ToAccount+'共：'+str(Amount)+'个'+AssetName))
                #privite
                if FromAccount=='cybex-jadegateway':
                    Titel = '转入'
                    CYBBalance = int(int(GetAccountBalance(items['op'][1]['to'],'1.3.0')['result'][0]['amount'])/AssetAccuracyDic['CYB'])
                    ETHBalance = int(GetAccountBalance(items['op'][1]['to'],'1.3.2')['result'][0]['amount'])/AssetAccuracyDic['ETH']
                    FirstMessage = ToAccount+Titel+AssetName
                    SecondMessage = '剩余:'+str(CYBBalance)+'CYB\t'+str(ETHBalance)+'ETH'
                else:
                    Titel = '转出'
                    CYBBalance = int(int(GetAccountBalance(items['op'][1]['from'],'1.3.0')['result'][0]['amount'])/AssetAccuracyDic['CYB'])
                    ETHBalance = int(GetAccountBalance(items['op'][1]['from'],'1.3.2')['result'][0]['amount'])/AssetAccuracyDic['ETH']
                    FirstMessage = FromAccount+Titel+AssetName
                    SecondMessage = '剩余:'+str(CYBBalance)+'CYB\t'+str(ETHBalance)+'ETH'
                if (AssetName=='ETH' and Amount>=2) or (AssetName=='USDT'and Amount >= 100) or (AssetName=='BTC'and Amount >= 0.01):
                    WeChat(FirstMessage,str(Amount),blocktime[1],SecondMessage)
                else:
                    #Private
                    WeChat(FirstMessage,str(Amount),blocktime[1],SecondMessage,['ozndm6GpNENreIEjzmP2mdO6xa8I'])
                    #respone = requests.get("https://sc.ftqq.com/SCU35027T736ad3831359ed542a0128a611864a265bd83348cd008.send?text={}&desp={}".format(FirstMessage,SecondMessage))

def run_test():
    accountID = '1.2.4733'#4733'831
    respone = scan_account(accountID,10)
    LatestBlock = respone[0]['block_num']    
    time.sleep(10)
    while True:
        num = 10
        respone = scan_account(accountID,num)
        updateTransferRecord(respone,LatestBlock)
        print(LatestBlock)
        timesleep = 40-random.randint(0,20)
        print(timesleep)
        time.sleep(timesleep)
        LatestBlock = respone[0]['block_num']
#if __name__ == '__main__':
#    run_test()

