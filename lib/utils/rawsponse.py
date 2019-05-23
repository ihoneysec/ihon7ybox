# coding: utf-8
import requests
from setting import HEADERS, TIMEOUT, VERIFY, RETRY_CNT, STREAM
from lib.common.urlhandler import slashlessURL

requests.packages.urllib3.disable_warnings()


def get_raw_response(searchdomain):
    hack_payload_url = slashlessURL(searchdomain)
    try_cnt = 0
    resultStr = []
    while True:
        try:
            r = requests.get(hack_payload_url, headers=HEADERS, timeout=TIMEOUT, verify=VERIFY, stream=STREAM)
            rep = r.headers
            resultStr.append('HTTP/1.1 ' + str(r.status_code) + ' ' + str(r.reason))
            for k, v in rep.items():
                resultStr.append('\r\n' + str(k) + ': ' + str(v))
            return resultStr
        except Exception as e:
            print(e)
            try_cnt += 1
            if try_cnt >= RETRY_CNT:
                return


if __name__ == '__main__':
    # print(get_raw_response('https://www.51oz.com'))
    # print(get_raw_response('https://www.shipuxiu.com'))
    print(get_raw_response('https://www.51oz.com'))
