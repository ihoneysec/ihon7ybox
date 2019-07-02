# coding: utf-8
import requests
from setting import HEADERS, TIMEOUT, VERIFY, RETRY_CNT, STREAM
from lib.common.urlhandler import addslashless
from lib.core.threads import RESULT_REPORT

requests.packages.urllib3.disable_warnings()


def verify(arg, result_report, **kwargs):
    hack_payload_url = addslashless(arg)
    try_cnt = 0
    resultStr = []
    while True:
        try:
            r = requests.get(hack_payload_url, headers=HEADERS, timeout=TIMEOUT, verify=VERIFY, stream=STREAM)
            rep = r.headers
            resultStr.append('HTTP/1.1 ' + str(r.status_code) + ' ' + str(r.reason))
            for k, v in rep.items():
                resultStr.append('\r\n' + str(k) + ': ' + str(v))
            if resultStr:
                result_report['raw_response'] = resultStr
                # print(result_report['raw_response'])
            else:
                result_report['raw_response'] = ['源站响应头获取异常']
            return result_report
        except Exception as e:
            print(e)
            try_cnt += 1
            if try_cnt >= RETRY_CNT:
                return ['源站响应头获取异常']


if __name__ == '__main__':
    print(verify('www.shaipu.com', RESULT_REPORT))
