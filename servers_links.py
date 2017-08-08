import hashlib
import xml.etree.ElementTree as ET
import itchatmp
from flask import Flask, request
import time
from tornado import gen
import logging
import pymongo
from subprocess import call
import os
import face

itchatmp.set_logging(showOnCmd=True, loggingFile=None, loggingLevel=logging.INFO)
itchatmp.update_config(itchatmp.WechatConfig(
    token='links',
    appId='wxff879408144bcc84',
    appSecret='a54fee27d6dc7ef7203a1bb805ef9631'
))


app = Flask(__name__)
app.debug = True
count = 0

@itchatmp.access_token
def get_access_token(accessToken=None):
    return accessToken


@app.route('/back')
def back():
    return 'none'


@app.route('/', methods=['GET', 'POST'])
def it_index():
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
                return reply_text(fromUser, toUser, "弹幕姬发动中")
            return reply_text(fromUser, toUser, reply(1, content))
        elif msgType == "image":
            image_url = xml.find('MediaId').text
            num = save_image(image_url)
            face.detect(num)
            return reply_image(fromUser, toUser, num)
        else:
            return reply_text(fromUser, toUser, "我只懂文字")


@app.route("/ok")
def ok():
    return "The server is working"


def save_image(image_url):
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
    count += 1
    return count - 1


def reply_text(to_user, from_user, content):
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


def reply_image(to_user, from_user, image_id):
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
    """.format(to_user, from_user, int(time.time() * 1000), upload(image_id))


def upload_image(image_id):
    r = itchatmp.messages.upload(itchatmp.content.IMAGE, './image/{}.jpg'.format(count))
    if r:
        print(r['media_id'])
        return r['media_id']
    else:
        print('Failed: \n%s' % r)


def reply(openid, msg):
    #简单地翻转一下字符串就回复用户
    return msg[::-1]


if __name__ == '__main__':
    # r = itchatmp.messages.upload(itchatmp.content.IMAGE, 'image.jpg')
    # if r:
    #     print(r['media_id'])
    # else:
    #     print('Failed: \n%s' % r)
    r = get_access_token()
    print(r)
    app.run(host="0.0.0.0", port=80)