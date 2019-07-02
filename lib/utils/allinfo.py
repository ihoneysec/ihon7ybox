# coding:utf-8
import requests
from lib.core.threads import main
from lib.core.threads import RESULT_REPORT
import datetime

requests.packages.urllib3.disable_warnings()


def get_all_info(rawdomain):
    """
    功能: 返回解析IP、原始响应头、CDN/WAF、旁站信息、多线程查询
    TODO: 增加CMS指纹识别、端口扫描
    """
    RESULT_REPORT['rawdomain'] = rawdomain
    startTime = datetime.datetime.now()
    main([rawdomain])
    delta = int((datetime.datetime.now() - startTime).total_seconds())
    RESULT_REPORT['total_seconds'] = str(delta)
    print("[*] total {0} seconds".format(str(delta)))

    if RESULT_REPORT:
        print(RESULT_REPORT)
        return RESULT_REPORT


if __name__ == '__main__':
    get_all_info('www.shaipu.com')
