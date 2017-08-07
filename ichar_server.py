#!/usr/bin/env python
# coding: utf-8
from flask import Flask
import requests
import re
import json

app = Flask(__name__)
appid = "wxff879408144bcc84"
secret = "a54fee27d6dc7ef7203a1bb805ef9631"
html = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="+appid+"&secret="+secret
html2 = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token="
requ = requests.get(html)
acess_keys = requ.json().get('access_token')
html2 += acess_keys
body = {"age": 22,
        "__module__": "Person",
        "__class__": "Person",
         "name": "Peter"}

b = requests.post(html2, json=body)
print(b.text)