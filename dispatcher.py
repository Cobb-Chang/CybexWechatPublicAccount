#! /usr/bin python
# coding: utf8
import sys
from wechatpy.replies import TextReply, ImageReply
import time
import json
from CybexFunction import *
import xml.etree.ElementTree as ET
from robot import *



class MsgDispatcher(object):
    """
    根据消息的类型，获取不同的处理返回值
    """

    def __init__(self, msg):
        self.msg = msg
        self.handler = MsgHandler(self.msg)

    def dispatch(self):
        self.result = ""  # 统一的公众号出口数据
        if self.msg.type == "text":
            self.result = self.handler.textHandle()
        elif self.msg.type == "voice":
            self.result = self.handler.voiceHandle()
        elif self.msg.type == 'image':
            self.result = self.handler.imageHandle()
        elif self.msg.type == 'video':
            self.result = self.handler.videoHandle()
        elif self.msg.type == 'shortvideo':
            self.result = self.handler.shortVideoHandle()
        elif self.msg.type == 'location':
            self.result = self.handler.locationHandle()
        elif self.msg.type == 'link':
            self.result = self.handler.linkHandle()
        elif self.msg.type == 'event':
            self.result = self.handler.eventHandle()
        return self.result


class MsgHandler(object):
    """
    针对type不同，转交给不同的处理函数。直接处理即可
    """

    def __init__(self, msg):
        self.msg = msg
        self.time = int(time.time())

    def textHandle(self, user='', master='', time='', content=''):
        template = """
        <xml>
             <ToUserName><![CDATA[{}]]></ToUserName>
             <FromUserName><![CDATA[{}]]></FromUserName>
             <CreateTime>{}</CreateTime>
             <MsgType><![CDATA[text]]></MsgType>
             <Content><![CDATA[{}]]></Content>
         </xml>
        """
        # 对用户发过来的数据进行解析，并执行不同的路径
        try:
            response = get_response_by_keyword(self.msg.content)
            if response['type'] == "image":
                result = self.imageHandle(response['content'])
            elif response['type'] == "music":
                data = response['content']
                result = self.musicHandle(data['title'], data['description'], data['url'], data['hqurl'])
            elif response['type'] == "news":
                items = response['content']
                result = self.newsHandle(items)
            # 这里还可以添加更多的拓展内容
            else:
                CYB = MyCybex()
                RecMsg = self.msg.content.split(" ")
                if len(RecMsg)==1:
                    responseCYB = CYB.GetAccountBalanceByName(RecMsg[0],'CYB')
                    if responseCYB != 'Error':
                        responseETH = CYB.GetAccountBalanceByName(RecMsg[0],'ETH')
                        responseUSDT = CYB.GetAccountBalanceByName(RecMsg[0],'USDT')
                        responseBTC = CYB.GetAccountBalanceByName(RecMsg[0],'BTC')
                        result = TextReply(content="该账户有：\n"+str(responseCYB)+'CYB\n'+str(responseETH)+'ETH\n'+str(responseUSDT)+'USDT\n'+str(responseBTC)+'BTC', message=self.msg)
                    else:
                        result = TextReply(content="目前支持的命令有：大户持仓排行（十天更新一次）。或者输入账号，查询账户资产信息(crypto-vault CYB)", message=self.msg)
                elif len(RecMsg)==2:
                    response = CYB.GetAccountBalanceByName(RecMsg[0],RecMsg[1].upper())
                    if response != 'Error':
                        result = TextReply(content="该账户有：\n"+str(response)+RecMsg[1].upper(),message = self.msg)
                    else:
                        result = TextReply(content="请输入正确的账号和资产", message=self.msg)
                else:
                    result = TextReply(content="目前支持的命令有：大户持仓排行（十天更新一次）。或者输入账号，查询账户资产信息(crypto-vault CYB)", message=self.msg)
        except Exception as e:
            with open("./debug.log", 'a') as f:
               f.write("text handler:"+str(e))
               f.close()
        return result

    def musicHandle(self, title='', description='', url='', hqurl=''):
        template = """
        <xml>
             <ToUserName><![CDATA[{}]]></ToUserName>
             <FromUserName><![CDATA[{}]]></FromUserName>
             <CreateTime>{}</CreateTime>
             <MsgType><![CDATA[music]]></MsgType>
             <Music>
             <Title><![CDATA[{}]]></Title>
             <Description><![CDATA[{}]]></Description>
             <MusicUrl><![CDATA[{}]]></MusicUrl>
             <HQMusicUrl><![CDATA[{}]]></HQMusicUrl>
             </Music>
             <FuncFlag>0</FuncFlag>
        </xml>
        """
        response = template.format(self.msg.user, self.msg.master, self.time, title, description, url, hqurl)
        return response

    def voiceHandle(self):
        response = get_turing_response(self.msg.recognition)
        result = self.textHandle(self.msg.user, self.msg.master, self.time, response)
        return result

    def imageHandle(self,mediaid=''):
        result = ImageReply(media_id=mediaid, message=self.msg)
        return result

    def videoHandle(self):
        return 'video'

    def shortVideoHandle(self):
        return 'shortvideo'

    def locationHandle(self):
        return 'location'

    def linkHandle(self):
        return 'link'

    def eventHandle(self):
        return 'event'

    def newsHandle(self, items):
        # 图文消息这块真的好多坑，尤其是<![CDATA[]]>中间不可以有空格，可怕极了
        articlestr = """
        <item>
            <Title><![CDATA[{}]]></Title>
            <Description><![CDATA[{}]]></Description>
            <PicUrl><![CDATA[{}]]></PicUrl>
            <Url><![CDATA[{}]]></Url>
        </item>
        """
        itemstr = ""
        for item in items:
            itemstr += str(articlestr.format(item['title'], item['description'], item['picurl'], item['url']))

        template = """
        <xml>
            <ToUserName><![CDATA[{}]]></ToUserName>
            <FromUserName><![CDATA[{}]]></FromUserName>
            <CreateTime>{}</CreateTime>
            <MsgType><![CDATA[news]]></MsgType>
            <ArticleCount>{}</ArticleCount>
            <Articles>{}</Articles>
        </xml>
        """
        result = template.format(self.msg.user, self.msg.master, self.time, len(items), itemstr)
        return result