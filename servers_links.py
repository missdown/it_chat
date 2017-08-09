import hashlib
import xml.etree.ElementTree as ET
import itchatmp
from flask import Flask, request
import time
from tornado import gen
import logging
import pymongo
import os
from subprocess import call


itchatmp.set_logging(showOnCmd=True, loggingFile=None, loggingLevel=logging.INFO)
itchatmp.update_config(itchatmp.WechatConfig(
    token='links',
    appId='wxff879408144bcc84',
    appSecret='a54fee27d6dc7ef7203a1bb805ef9631'
))


app = Flask(__name__)
app.debug = True


class responce_deal:

    def __init__(self):
        if [True for i in os.listdir('./') if i == 'save.txt']:
            pass
        else:
            with open('save.txt', 'w') as fp:
                fp.write('{}'.format(0))
        with open('save.txt', 'r') as fp:
            self.count = fp.read()
            print(self.count)
        self.access_taken = get_access_token()
        self.local_hour = time.localtime()[3]

    def save_image(self,image_url):
        if [True for i in os.listdir('./') if i == 'image']:
            pass
        else:
            os.mkdir("./image")
        r = itchatmp.messages.download(image_url)
        if 'File' in r:
            with open(r.get('./image', '{}.jpg'.format(count)), 'wb') as f:
                f.write(r['File'].getvalue())
        else:
            print(r)

    def reply_text(self,to_user, from_user, content):
        """
        以文本类型的方式回复请求
        :param to_user:
        :param from_user:
        :param content:
        :return:
        """
        return """
        <xml>
            <ToUserName><![CDATA[{}]]></ToUserName>
            <FromUserName><![CDATA[{}]]></FromUserName>
            <CreateTime>{}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{}]]></Content>
        </xml>
        """.format(to_user, from_user,
                   int(time.time() * 1000), content)

    def reply_image(self, to_user, from_user, image_id):
        return """
        <xml>
            <ToUserName><![CDATA[{}]]></ToUserName>
            <FromUserName><![CDATA[{}]]></FromUserName>
            <CreateTime>{}</CreateTime>
            <MsgType><![CDATA[image]]></MsgType>
            <Image>
            <MediaId><![CDATA[{}]]></MediaId>
            </Image>
        </xml>
        """.format(to_user, from_user, int(time.time() * 1000), upload_image(image_id))

    def upload_image(self, image_id):
        r = itchatmp.messages.upload(itchatmp.content.IMAGE, './predictions.jpg')
        if r:
            print(r['media_id'])
            return r['media_id']
        else:
            print('Failed: \n%s' % r)
        self.count += 1
        with open('save.txt', 'w') as fp:
            fp.write('{}'.format(self.count))

    def reply(self, openid, msg):
        # 简单地翻转一下字符串就回复用户
        return msg[::-1]

    def save_access_taken(self):
        if time.localtime()[3] == self.local_hour:
            return self.access_taken
        else:
            self.access_taken = get_access_token()
            self.local_hour = time.localtime()[3]
            return self.access_taken


@itchatmp.access_token
def get_access_token(accessToken=None):
    return accessToken


@app.route('/back')
def back():
    return 'none'


@app.route('/', methods=['GET', 'POST'])
def it_index():
    deal = responce_deal()
    if request.method == 'GET':
        token = 'links'  # 微信配置所需的token
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        s = ''.join(sorted([timestamp, nonce, token]))
        sha1 = hashlib.sha1()
        sha1.update(bytes(s, "utf8"))
        if sha1.hexdigest() == signature:
            return echostr
    else:
        xml = ET.fromstring(request.data)
        toUser = xml.find('ToUserName').text
        fromUser = xml.find('FromUserName').text
        msgType = xml.find("MsgType").text
        createTime = xml.find("CreateTime")
        if msgType == "text":
            content = xml.find('Content').text
            if content == "弹幕发送":
                return deal.reply_text(fromUser, toUser, "弹幕姬发动中")
            return deal.reply_text(fromUser, toUser, reply(1, content))
        elif msgType == "image":
            image_url = xml.find('MediaId').text
            if os.path.getsize('{}.jpg'.format(num)) / 1000 / 1000 > 2:
                return deal.reply_text(fromUser, toUser, "图片太大了哦")
            call('./darknet detector test cfg/voc.data cfg/tiny-yolo-voc.cfg tiny-yolo-voc.weights -c 0 -thresh 0.15 ./{}.jpg'.format(deal.count), shell=True)
            return deal.reply_image(fromUser, toUser, deal.count)
        else:
            return deal.reply_text(fromUser, toUser, "不明白哦")


@app.route("/status")
def ok():
    return "<h1>The server is working</h1>"


if __name__ == '__main__':
    # r = itchatmp.messages.upload(itchatmp.content.IMAGE, 'image.jpg')
    # if r:
    #     print(r['media_id'])
    # else:
    #     print('Failed: \n%s' % r)
    app.run(host="0.0.0.0", port=80)