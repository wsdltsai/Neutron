# -*- coding: utf-8 -*-
import requests
import uuid
import urllib
import json
import time
from user_config import user_config, set_config


"""
提供与Azure的API交互
"""


ISSUETOKEN_URL = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken"
RECOGNICE_URL = "https://speech.platform.bing.com/recognize"
SYNTHESIZE_URL = "https://speech.platform.bing.com/synthesize"
KEY = "c622adb2893e438796177fadace4a2f2"
X_SEARCH_APPID = "e2d7d03b4855434eb05095688ec4bc65"


def gen_token():
    """
    使用key去交换一个token 这里每次生成 可用缓存
    """
    new_token = issue_token()
    return new_token


def issue_token():
    ret = requests.post(
        ISSUETOKEN_URL,
        headers={
            "Ocp-Apim-Subscription-Key": KEY
        }
    )
    return ret.content


def recognize(file):
    """
    传入音频file obj 返回text
    """
    headers = {
        "Host": "speech.platform.bing.com",
        "Content-Type": "audio/wav",
        "Authorization": "Bearer %s" % gen_token()
    }
    data = {
        "scenarios": "catsearch",
        "appid": "D4D52672-91D7-4C74-8AD8-42B1D98141A5",
        "locale": "en-US",
        "device.os": "wp7",
        "version": "3.0",
        "format": "json",
        "requestid": "1d4b6030-9099-11e0-91e4-0800200c9a99",
        "instanceid": uuid.uuid4()
    }
    query_string = urllib.urlencode(data)
    ret = requests.post(
        RECOGNICE_URL + "?%s" % query_string,
        headers=headers,
        data=file
        # open("Hack.wav", 'rb')
    )
    ret = json.loads(ret.content)
    if ret['header']['status'] == 'success':
        return ret['results'][0]['name']
    else:
        return "fail to recognize"


def synthesize(text, lang='en-US'):
    """
    传入text 返回保存的音频文件名
    """
    headers = {
        "Host": "speech.platform.bing.com",
        "Content-Type": "application/ssml+xml",
        "Authorization": "Bearer %s" % gen_token(),
        "X-Microsoft-OutputFormat": "riff-8khz-8bit-mono-mulaw",
        "X-Search-Appid": X_SEARCH_APPID,
        "X-Search-ClientID": str(uuid.uuid4()).replace("-", ""),
    }
    gender = user_config.get('gender')
    print 'use gender: %s' % gender
    # set_config('gender', 'Male')
    if gender == 'Female':
        service_name = 'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)'
    else:
        service_name = "Microsoft Server Speech Text to Speech Voice (en-US, BenjaminRUS)"
    body = "<speak version='1.0' xml:lang='en-us'><voice xml:lang='%s' xml:gender='%s' name='%s'>%s</voice></speak>" % (lang, gender, service_name, text)
    ret = requests.post(
        url=SYNTHESIZE_URL,
        headers=headers,
        data=body
    )
    if ret.status_code == 200:
        save_file_name = "voice%s.wav" % str(time.time())[:10]
        with open("app/return_voice/%s" % save_file_name, "wb") as f:
            f.write(ret.content)
        return "ok", save_file_name
    else:
        return "fail", ""


if __name__ == '__main__':
    from IPython import embed
    embed()