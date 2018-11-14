# -*- coding: utf-8 -*-
import datetime
import requests
import json
 
class WeChat(object):
    def __init__(self,Title,Amount='',Time='',Message='',openid = ['1']):
        self.Title = Title
        self.Amount=Amount
        self.Time=Time
        self.Message = Message
        self.access_token = None
        self.openid = []
        self.get_token()
        if openid[0] == '1':
            self.get_openid()
        else:
            self.openid = openid
        self.post_data()

    def call(method, params):
        data = {
        "jsonrpc":"2.0",
        "method":method, 
        "params":params,
        "id":1}
        jsondata = json.dumps(data)
        respone = requests.post(apilist[random.randint(0,len(apilist)-1)], data=jsondata)
        return json.loads(respone.text)    

    def get_token(self):
        payload = {
                'grant_type': 'client_credential',
                'appid': 'wxca2f87138f95d1ae',
                'secret':'790c7d4270ed78530a484f7ce4ad3f29'
                }
        url="https://api.weixin.qq.com/cgi-bin/token?"
        try:
            respone=requests.get(url, params=payload, timeout=50)
            self.access_token=respone.json().get("access_token")
            #content="{'access_token':"+str(access_token)+",'time':"+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"}"
            #return access_token
        except Exception as e:
            with open("./debug.log", 'a') as f:
                f.write("text handler:"+str(e))
                f.close()
 
    def post_data(self):
        data={
               "touser":self.openid[0],
               "template_id":"b-3zx5D68QU30SoVI4Hv6QxFbIk_5gwjm8p6oLAznFs",#模板ID
               #"url":"www.baidu.com",
               # "miniprogram":{
               #   "appid":"wx67afc56d7f6cfac0",  #待使用上线小程序appid
               #   "path":"pages/reserve/mgr/mgr"
               # },
               "data":{
                       "first": {
                           "value":self.Title,
                           "color":"#173177"
                       },
                       "keyword1":{
                           "value":self.Amount,
                           "color":"#173177"
                       },
                       "keyword2": {
                           "value":self.Time,
                           "color":"#173177"
                       },
                       "remark":{
                           "value":self.Message,
                           "color":"#173177"
                       }
               }
           }
        try:

            url="https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+str(self.access_token)
            for openid in self.openid: 
                data["touser"] = openid
                json_template=json.dumps(data)
                respone=requests.post(url,data=json_template, timeout=50)
                errcode=respone.json().get("errcode")
                if(errcode!=0):
                    print("模板消息发送失败")
                    print("test--",respone.json())
        except Exception as e:
            with open("./debug.log", 'a') as f:
               f.write("text handler:"+str(e))
               f.close()

    def get_openid(self):
        url="https://api.weixin.qq.com/cgi-bin/user/get?access_token="+str(self.access_token)
        respone=requests.post(url, timeout=50)
        respone = json.loads(respone.text)
        nextOpenid = respone["next_openid"]
        self.openid = respone['data']['openid']

    