# coding:utf-8
import requests
from setting import HEADERS, RETRY_CNT, TIMEOUT, VERIFY
import json


def getIpInfo(arg):
    ipInfoResult = ''
    try:
        url = "http://ip.taobao.com/service/getIpInfo.php?ip=%s" % str(arg[0])
        s = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=VERIFY).text
        jsondata = json.loads(s)

        if jsondata['code'] == 1:
            arg.append('getIpInfoError')
        else:
            if jsondata['data']['region'] and jsondata['data']['region'] != 'XX':
                ipInfoResult += jsondata['data']['region']
            if jsondata['data']['city'] and jsondata['data']['city'] != 'XX':
                ipInfoResult += ' ' +jsondata['data']['city']
            if jsondata['data']['isp'] and jsondata['data']['isp'] != 'XX':
                ipInfoResult += ' ' +jsondata['data']['isp']
            arg.append(ipInfoResult)
        if arg:
            return arg
    except Exception as e:
        print(e)

if __name__ == '__main__':
    print(getIpInfo(['61.160.212.73']))
    print(getIpInfo(['123.56.10.70']))