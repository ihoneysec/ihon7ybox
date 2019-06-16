# -*- coding: utf-8 -*-
import requests
import re
from lib.common.urlhandler import addslashless
from setting import RETRY_CNT, TIMEOUT, VERIFY

requests.packages.urllib3.disable_warnings()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', }


def get_cdn_waf(rawdomain):
    """
    模仿云悉部分识别方式
    /yunsee_detect.mdb
    /yunsee_detect.sql
    /yunsee_not_found_test
    /9d4731bc16414/yunsee_best_recognizer.jpg
    """
    u_list = ['',
              'wdocnbuqefhidc132fwqcs_not_found_test',
              '9d47414/wdohidqcs_best_recognizer.jpg',
              'robots.txt~',     # sofedog
              'robots.txt.bak',  # yunsuo
              'wdocnbuqefhidc132fwqcs.mdb',
              'wdocnbuqefhidc132fwqcs.sql',
              'robots.txt/.php',
              # 'user/City_ajax.aspx?CityId=1\' union all select UserNum,UserNum from dbo.fs_sys_User where UserName=\'admin'
              # 明显的注入请求会触发阿里云防火墙服务器屏蔽向外80端口的访问
              ]

    wafcdnlist = []

    for u in u_list:
        url = addslashless(rawdomain) + u
        print(url)
        try_cnt = 0
        while True:
            try:
                global page_get
                global headers_get
                s = requests.Session()
                r = s.get(url, headers=HEADERS, timeout=TIMEOUT, verify=VERIFY)
                page_get = str(r.content)
                headers_get = str(r.headers)
                # print(headers_get)
                break
            except Exception as e:
                print(e)
                try_cnt += 1
                if try_cnt >= RETRY_CNT:
                    break
                    # return ['未检测到CDN或WAF']

        print('checking...')
        if page_get or headers_get:
            pass
        else:
            continue
        """
        Xampps_Request: Server: D=44676 t=1558071443078185 l=-1.00/-1.00/-1.00 b=2 i=97
        Xampps_Info: Xampps Tuesday(104979058) Apache PHP MySql FileZilla
        """

        waf_dic = {
            '阿里云WAF': [
                'retval = re.search(r"errors.aliyun.com", page_get, re.I)',
            ],
            '阿里云CDN': [
                'retval = re.search(r"aliyungf_/", headers_get, re.I)',
                'retval = re.search(r"kunlun[\d]?\.cn", headers_get, re.I)',
                'retval = re.search(r"cache[\d]{1,2}\.", headers_get, re.I)',
                'retval = re.search(r"Ali-Swift-Global-Savetime", headers_get, re.I)',
            ],
            '宝塔': [
                'retval = re.search(r"\www.bt\.cn", page_get, re.I)',
                'retval = re.search(r"//www\.bt\.cn/stop\.png", page_get, re.I)',
                'retval = re.search(r".title{background: #20a53a;color: #fff;font-size: 16px;height: 40px;line-height: 40px;padding-left: 20px;}", page_get, re.I)'
            ],
            # www.cdedu.cn
            # www.hbggzy.cn CNAME 4eb7b2bcf8ec4610.360cloudwaf.com
            '主机360/奇安信waf': [
                'retval = re.search(r"360wzws", headers_get, re.I)',
                'retval = re.search(r"X-Powered-By-ANYU", headers_get, re.I)',
                'retval = re.search(r"anyu.360.net", headers_get, re.I)',
                'retval = re.search(r"zhuji\.360\.cn", headers_get, re.I)',
                'retval = re.search(r"X-Safe-Firewall", headers_get, re.I)',
                'retval = re.search(r"wangzhan\.360\.cn", headers_get, re.I)',
                'retval = re.search(r"wangzhan\.qianxin\.com", headers_get, re.I)',
                'retval = re.search(r"X-Powered-By-WZWS", headers_get, re.I)',
                'retval = re.search(r"X-Powered-By-360wzb", headers_get, re.I)',
                'retval = re.search(r"WZWS-RAY", headers_get, re.I)',
                'retval = re.search(r"/wzws-waf-cgi/", page_get, re.I)',
                'retval = re.search(r"anyu\.qianxin\.com", headers_get, re.I)',
                'retval = re.search(r"qianxin-waf", headers_get, re.I)',
            ],
            '上海云盾CDN': [
                'retval = re.search(r"YUNDUN", headers_get,re.I)',
                'retval = re.search(r"WAF/2\.4-12\.1", headers_get,re.I)',
                'retval = re.search(r"yd_cookie", headers_get,re.I)'
            ],
            '云锁/网防G01': [
                'retval = re.search(r"security_session_verify",headers_get, re.I)',
                'retval = re.search(r"security_session_mid_verify", headers_get, re.I)',
                'retval = re.search(r"yunsuo_session",headers_get, re.I)',
                'retval = re.search(r"yunsuologo", page_get, re.I)',
                'retval = re.search(r"tip1 red", page_get, re.I)',
                'retval = re.search(r"网防G01提示:", page_get, re.I)',

            ],
            # www.cheshi.com vo.aicdn.com ['www.cheshi.com','cheshi-www.b0.aicdn.com'] ['43.230.89.187']
            '又拍云CDN': [
                'retval = re.search(r"pcw-cn-", headers_get, re.I)',
            ],
            # www.ywnews.cn jhcloud85.cache.saaswaf.com	['www.ywnews.cn','ywnews-cn.cname.saaswaf.com']
            # '玄武盾CDN': [
            #     'retval = re.search(r"pcw-cn-", headers_get, re.I)',
            # ],
            'D盾': [
                'retval = re.search(r"_d_id", headers_get, re.I)',
                'retval = re.search(r"_D_SID", headers_get, re.I)'
            ],
            # www.shaipu.com
            # Set-Cookie: sdwaf-test-item=363c185603560307010007050053500c035501025c5000510f515d54560000; path=/; HttpOnly
            # X-Powered-By: SDWAF
            'sdwaf': [
                'retval = re.search(r"SDWAF ", headers_get, re.I)',
                'retval = re.search(r"sdwaf-test-item", headers_get, re.I)'
            ],
            '腾讯云WAF': [
                'retval = re.search(r"waf\.tencent-cloud.com", page_get, re.I)',
                'retval = re.search(r"//console.qcloud.com/guanjia/waf/config", page_get, re.I)'
            ],
            '百度云加速CDN': [
                'retval = re.search(r"fhl", headers_get, re.I)',
                'retval = re.search(r"yunjiasu-nginx", headers_get,re.I)'
            ],
            'cloudflare': [
                'retval = re.search(r"cloudflare", headers_get,re.I)',
                'retval = re.search(r"\A__cfduid=", headers_get,re.I)',
                'retval = re.search(r"cf-ray", headers_get,re.I)',
                'retval = re.search(r"cloudflare-nginx", headers_get,re.I)',
                'retval = re.search(r"\A__cfduid=",headers_get, re.I)',
                'retval = re.search(r"__cfduid=",headers_get, re.I)',
                'retval = re.search(r"CloudFlare Ray ID:|var CloudFlare=", page_get, re.I)',
                'retval = re.search(r"Attention Required|Cloudflare", page_get, re.I)',
                'retval = re.search(r"Sorry, you have been blocked", page_get, re.I)',
                'retval = re.search(r"CloudFlare Ray ID:|var CloudFlare=", page_get, re.I)',
                'retval = re.search(r"CLOUDFLARE_ERROR_500S_BOX", page_get, re.I)',
                'retval = re.search(r"::CAPTCHA_BOX::", page_get, re.I)',
                'retval = re.search(r"Attention Required|Cloudflare", page_get, re.I)'
            ],
            '加速乐': [
                'retval = re.search(r"jiasule-WAF", headers_get,re.I)',
                'retval = re.search(r"__jsluid=",headers_get, re.I)',
                'retval = re.search(r"jsl_tracking",headers_get, re.I)',
                'retval = re.search(r"static\.jiasule\.com/static/js/http_error\.js", page_get, re.I)',
                'retval = re.search(r"X-Via-JSL", headers_get, re.I)',
                'retval = re.search(r"notice-jiasule", page_get, re.I)',
            ],
            '安全狗': [
                'retval = re.search(r"WAF/2\.0",headers_get, re.I)',
                'retval = re.search(r"Safedog", headers_get,re.I)',
                'retval = re.search(r"safedog", headers_get, re.I)',
                'retval = re.search(r"safedog-flow-item=", headers_get, re.I)',
                'retval = re.search("safedogsite/broswer_logo.jpg", page_get, re.I)',
                'retval = re.search("404.safedog.cn/sitedog_stat.html", page_get, re.I)',
                'retval = re.search("404.safedog.cn/images/safedogsite/head.png", page_get, re.I)'
            ],
            '安全宝': [
                # 'retval = re.search(r"MISS", headers_get, re.I)',
                'retval = re.search(r"/aqb_cc/error/", page_get, re.I)',
            ],
            'YxLinkWAF(安恒?)': [
                'retval = re.search(r"<body><div class=\'page\'><div class=\'container\'><div class=\'main\'><div class=\'infobox\'><div class=\'infobox-shadow\'></div><div class=\'infobox-texts\'><div class=\'it-title\'>", page_get, re.I)'
            ],
            'WDCP': [
                'retval = re.search(r"://www.wdlinux.cn/wdcp", page_get, re.I)'
            ],
            # http://www.ciqinghui.com/data/
            'AMH主机面板': [
                'retval = re.search(r"://amh.sh", page_get, re.I)'
            ],
            'WTS-WAF': [
                'retval = re.search(r"\Awts/", headers_get,re.I)',
                'retval = re.search(r"wts/", headers_get,re.I)',
                'retval = re.search(r"wts/1.2", headers_get,re.I)'
            ],
            '乌云盾': [
                'retval = re.search(r"wafcloud\.net", page_get,re.I)',
            ],
            # https://www.54cn.net/
            '蓝盾': [
                'retval = re.search(r"BLUEDON", page_get,re.I)',
            ],
            '创宇盾': [
                'retval = re.search(r"www\.365cyd\.com", page_get,re.I)',
            ],
            '南昌邦腾CDN': [
                'retval = re.search(r"www\.cdnbest\.com", headers_get,re.I)',
            ],
            '可能存在WAF': [
                'retval = re.search(r"X-Via:", headers_get,re.I)',
            ],
            'armor': [
                'retval = re.search(r"This request has been blocked by website protection from Armor", page_get, re.I)'
            ],
            'aws': [
                'retval = re.search(r"\bAWS", headers_get,re.I)'
            ],
            'barracuda': [
                'retval = re.search(r"\Abarra_counter_session=",headers_get, re.I)',
                'retval = re.search(r"(\A|\b)barracuda_",headers_get, re.I)'
            ],
            'bigip': [
                'retval = re.search(r"\ATS\w{4,}=",headers_get, re.I)',
                'retval = re.search(r"BigIP|BIGipServer",headers_get, re.I)',
                'retval = re.search(r"BigIP|BIGipServer", headers_get,re.I)',
                'retval = re.search(r"\AF5\Z", headers_get,re.I)'
            ],
            'binarysec': [
                'retval = re.search(r"BinarySec", headers_get,re.I)'
            ],
            'blockdos': [
                'retval = re.search(r"BlockDos\.net", headers_get,re.I)'
            ],
            'ciscoacexml': [
                'retval = re.search(r"ACE XML Gateway", headers_get,re.I)'
            ],
            'cloudfront': [
                'retval = re.search(r"cloudfront", headers_get,re.I)',
                'retval = re.search(r"cloudfront", headers_get,re.I)'
            ],
            'comodo': [
                'retval = re.search(r"Protected by COMODO WAF", headers_get,re.I)'
            ],
            'ibm': [
                'retval = re.search(r"\A(OK|FAIL)", headers_get, re.I)',
                'retval = re.search(r"^(OK|FAIL)", headers_get, re.I)'
            ],
            'denyall': [
                'retval = re.search(r"\Asessioncookie=",headers_get, re.I)',
                'retval = re.search(r"\ACondition Intercepted", page_get, re.I)'
            ],
            'dotdefender': [
                'retval = re.search(r"dotDefender Blocked Your Request", page_get, re.I)',
            ],
            'edgecast': [
                'retval = re.search(r"\AECDF", headers_get,re.I)'
            ],
            'expressionengine': [
                'retval = re.search(r"Invalid GET Data", page_get,re.I)',
            ],
            'fortiweb': [
                'retval = re.search(r"\AFORTIWAFSID=",headers_get, re.I)'
            ],
            'hyperguard': [
                'retval = re.search(r"\AODSESSION=",headers_get, re.I)'
            ],
            'incapsula': [
                'retval = re.search(r"incap_ses|visid_incap",headers_get, re.I)',
                'retval = re.search(r"Incapsula", headers_get, re.I)',
                'retval = re.search(r"Incapsula incident ID", page_get, re.I)',
            ],
            'isaserver': [
                'retval = re.search("The server denied the specified Uniform Resource Locator (URL). Contact the server administrator.", page_get, re.I)',
                'retval = re.search("The ISA Server denied the specified Uniform Resource Locator (URL)", page_get, re.I)'
            ],
            'kona': [
                'retval = re.search(r"Reference #[0-9a-f.]+", page_get, re.I)',
                'retval = re.search(r"AkamaiGHost", headers_get,re.I)'
            ],
            'modsecurity': [
                'retval = re.search(r"Mod_Security|NOYB", headers_get,re.I)',
                'retval = re.search(r"This error was generated by Mod_Security", page_get, re.I)'
            ],
            'netcontinuum': [
                'retval = re.search(r"\ANCI__SessionId=",headers_get, re.I)'
            ],
            'netscaler': [
                'retval = re.search(r"\Aclose", headers_get,re.I)',
                'retval = re.search(r"\A(ns_af=|citrix_ns_id|NSC_)",headers_get, re.I)',
                'retval = re.search(r"\ANS-CACHE",headers_get,re.I)'
            ],
            'newdefend': [
                'retval = re.search(r"newdefend", headers_get,re.I)'
            ],
            'nsfocus': [
                'retval = re.search(r"NSFocus", headers_get,re.I)'
            ],
            'paloalto': [
                'retval = re.search(r"Access[^<]+has been blocked in accordance with company policy", page_get, re.I)'
            ],
            'profense': [
                'retval = re.search(r"\APLBSID=",headers_get, re.I)',
                'retval = re.search(r"Profense", headers_get,re.I)'
            ],
            'radware': [
                'retval = re.search(r"Unauthorized Activity Has Been Detected.+Case Number:", page_get, re.I | re.S)'
            ],
            'requestvalidationmode': [
                'retval = re.search(r"ASP.NET has detected data in the request that is potentially dangerous", page_get, re.I)',
                'retval = re.search(r"Request Validation has detected a potentially dangerous client input value", page_get, re.I)'
            ],
            'safe3': [
                'retval = re.search(r"Safe3WAF",headers_get, re.I)',
                'retval = re.search(r"Safe3 Web Firewall", headers_get,re.I)'
            ],
            'secureiis': [
                'retval = re.search(r"SecureIIS[^<]+Web Server Protection", page_get, re.I)',
                'retval = re.search(r"http://www.eeye.com/SecureIIS/", page_get, re.I)',
                'retval = re.search(r"\?subject=[^>]*SecureIIS Error", page_get, re.I)'
            ],
            'senginx': [
                'retval = "SENGINX-ROBOT-MITIGATION" in (page_get)',
            ],
            'sitelock': [
                'retval = "SiteLock Incident ID" in (page_get)'
            ],
            'sonicwall': [
                'retval = "This request is blocked by the SonicWALL" in (page_get)',
                'retval = re.search(r"Web Site Blocked.+\bnsa_banner", page_get, re.I)',
                'retval = re.search(r"SonicWALL", headers_get,re.I)'
            ],
            'sophos': [
                'retval = "Powered by UTM Web Protection" in (page_get)'
            ],
            'stingray': [
                'retval = re.search(r"\AX-Mapping-",headers_get, re.I)'
            ],
            'sucuri': [
                'retval = re.search(r"Sucuri/Cloudproxy", headers_get,re.I)',
                'retval = re.search(r"Sucuri WebSite Firewall - CloudProxy - Access Denied", page_get,re.I)',
                'retval = re.search(r"Questions\?.+cloudproxy@sucuri\.net", (page_get))'
            ],
            'teros': [
                'retval = re.search(r"\Ast8(id|_wat|_wlf)",headers_get, re.I)'
            ],
            'trafficshield': [
                'retval = re.search(r"F5-TrafficShield", headers_get,re.I)',
                'retval = re.search(r"\AASINFO=",headers_get, re.I)'
            ],
            'urlscan': [
                'retval = re.search(r"Rejected-By-UrlScan",headers_get, re.I)',
                'retval = re.search(r"/Rejected-By-UrlScan", page_get, re.I)'
            ],
            'uspses': [
                'retval = re.search(r"Secure Entry Server", headers_get,re.I)'
            ],
            'varnish': [
                'retval = re.search(r"varnish\Z",headers_get,re.I)',
                'retval = re.search(r"varnish", headers_get,re.I)',
                'retval = re.search(r"\bXID: \d+", page_get)'
            ],
            'wallarm': [
                'retval = re.search(r"nginx-wallarm", headers_get,re.I)'
            ],
            'webknight': [
                'retval = re.search(r"WebKnight", headers_get,re.I)'
            ],
            'airlock': [
                'retval = re.search(r"\AAL[_-]?(SESS|LB)=",headers_get, re.I)'
            ],
        }
        # waf/cdn

        for k, v in waf_dic.items():  # python2 waf_dic.iteritems()
            for x in v:
                try:
                    global retval
                    exec(x, globals())
                    if retval:
                        if k not in wafcdnlist:
                            # print(k)
                            wafcdnlist.append(k)
                        continue
                except Exception as e:
                    print(e)
    if wafcdnlist:
        return wafcdnlist
    return ['未检测到CDN或WAF']


if __name__ == '__main__':
    print(get_cdn_waf('http://www.shaipu.com/'))
    # print(get_cdn_waf('http://www.cdedu.cn/'))
    # print(get_cdn_waf('http://www.xyaz.cn/'))
    # print(get_cdn_waf('http://www.legaldaily.com.cn/'))
    # print(get_cdn_waf('http://www.yundun.com/'))
    # print(get_cdn_waf('http://www.sjzpfb120.com/'))
    # print(get_cdn_waf('http://www.51g3.org/'))
    """
    返回
    http://www.yundun.com/ 发现WAF : YUNDUN
    http://www.sjzpfb120.com/ 发现WAF : D盾
    http://www.51g3.org/ 发现WAF : safedog
    """
