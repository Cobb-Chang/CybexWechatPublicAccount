import falcon
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message
from wechatpy.replies import TextReply, ImageReply
from wechatpy.messages import TextMessage
from dispatcher import *
from flask import Flask, request, make_response
from multiprocessing import Process
class Connect(object):

    def on_get(self, req, resp):
        query_string = req.query_string
        print(query_string)
        query_list = query_string.split('&')
        b = {}
        for i in query_list:
            b[i.split('=')[0]] = i.split('=')[1]

        try:
            check_signature(token='123456', signature=b['signature'], timestamp=b['timestamp'], nonce=b['nonce'])
            resp.body = (b['echostr'])
        except InvalidSignatureException:
            with open("./debug.log", 'a') as f:
                f.write("text handler:"+str(e))
                f.close()
            pass
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        
        try:
            xml = req.stream.read()
            msg = parse_message(xml)
            dispatcher = MsgDispatcher(msg)
            reply = dispatcher.dispatch()
            xml = reply.render()
            resp.body = (xml)
            resp.status = falcon.HTTP_200
        except Exception as e:
            with open("./debug.log", 'a') as f:
               f.write("text handler:"+str(e))
               f.close()

        
        '''
        xml = req.stream.read()
        msg = parse_message(xml)
        if msg.type == 'text':
            #msg.target = 'xa8Igh_34614a12efbd'
            reply = TextReply(content='source:'+msg.source+'   target:'+msg.target, message=msg)
            xml = reply.render()
            resp.body = (xml)
            resp.status = falcon.HTTP_200
        elif msg.type == 'image':
            reply = ImageReply(media_id=msg.media_id, message=msg)
            xml = reply.render()
            resp.body = (xml)
            resp.status = falcon.HTTP_200'''


app = falcon.API()
connect = Connect()
app.add_route('/connect', connect)



