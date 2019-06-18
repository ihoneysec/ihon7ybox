# coding:utf-8
import requests
from lib.utils.rawsponse import getRawResponse
from lib.utils.parseip import getIP
from lib.utils.cdnwaf import getCdnWAF
from lib.utils.pangzhan import getPzList

requests.packages.urllib3.disable_warnings()


def get_all_info(rawdomain, searchdomain):
    """
    功能: 返回解析IP、原始响应头、CDN/WAF、旁站信息
    TODO: 改成多线程查询、增加CMS指纹识别、端口扫描
    """
    result = {
        'rawdomain': rawdomain,
        'parse_ip': {'dhostname': '', 'daliaslist': ['None'], 'dipaddrlist': ['None']},  # 已完成
        'ip_city': 'None',
        'pz_number': 'None',
        'cdn_waf': ['未检测到CDN或WAF'],
        'raw_response': "源站响应头获取异常",
        'pz': {'city': '',
               'ipaddr': '',
               'pz_number': '',
               'pz_domains': []
               }
    }

    try:
        result['parse_ip'] = getIP(searchdomain)
        # print(result['parse_ip'])
    except Exception as e:
        print(e)

    try:
        result['raw_response'] = getRawResponse(rawdomain)
        # print(result['raw_response'])
    except Exception as e:
        print(e)

    try:
        result['cdn_waf'] = getCdnWAF(rawdomain)
        # print(result['cdn_waf'])
    except Exception as e:

        print(e)

    #try:
    #    result['pz'] = get_pzlist(searchdomain)
    #    # print(result['pz'])
    #except Exception as e:
    #    print(e)

    if result:
        print(result)
        return result
