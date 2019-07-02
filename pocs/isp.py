# coding:utf-8
import socket
import json
from lib.core.threads import RESULT_REPORT
from setting import HEADERS, RETRY_CNT, TIMEOUT, VERIFY
import requests


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
                ipInfoResult += ' ' + jsondata['data']['city']
            if jsondata['data']['isp'] and jsondata['data']['isp'] != 'XX':
                ipInfoResult += ' ' + jsondata['data']['isp']
            arg.append(ipInfoResult)
        if arg:
            return arg
        else:
            return arg
    except Exception as e:
        print(e)
        return arg


def verify(arg, result_report, **kwargs):
    try:
        result = socket.gethostbyname_ex(arg)
        if result:
            dhostname, daliaslist, dipaddrlist = result
            if len(dipaddrlist) == 1:
                ipPlus = getIpInfo(dipaddrlist)
                if ipPlus is not None:
                    ipInfo = ipPlus
                else:
                    ipInfo = dipaddrlist
            else:
                ipInfo = dipaddrlist
            if len(daliaslist) >= 1:
                parse_result = {'dhostname': dhostname, 'daliaslist': daliaslist, 'dipaddrlist': ipInfo}
            else:
                parse_result = {'dhostname': dhostname, 'daliaslist': ['None'], 'dipaddrlist': ipInfo}
            result_report['parse_ip'] = parse_result
            # print(result_report['parse_ip'])
            return result_report
    except Exception as e:
        print(e)
        return


if __name__ == '__main__':
    print(verify('www.shaipu.com', RESULT_REPORT))
