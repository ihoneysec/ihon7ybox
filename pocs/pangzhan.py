# coding:utf-8
import requests
import time
import chardet
from lxml import etree
from setting import MAXPAGE, PANGZHAN_HEADERS, VERIFY
from lib.core.threads import RESULT_REPORT

requests.packages.urllib3.disable_warnings()


def verify(arg, result_report, **kwargs):
    domain = arg.strip()
    pz_result = {
        'city': 'None',
        'ipaddr': 'None',
        'pz_number': 'None',
        'pz_domains': []
    }

    time.sleep(0.5)

    try:
        aizhan = 'https://dns.aizhan.com/'

        if len(domain) > 24:
            pz_result['info'] = None
            return pz_result

        search_url = aizhan + domain + '/'
        # print(search_url)
        r = requests.get(search_url, headers=PANGZHAN_HEADERS, verify=VERIFY)
        #     /html/body/div[4]/div[2]/ul/li[4]/span
        x1 = '/html/body/div[4]/div[2]/ul/li[4]/span/text()'
        ipa = '/html/body/div[4]/div[2]/ul/li[2]/strong/text()'
        city = '/html/body/div[4]/div[2]/ul/li[3]/strong/text()'
        currdomain = '/html/body/div[4]/div[2]/ul/li[1]/strong/text()'
        codesty = chardet.detect(r.content)
        rep = r.content.decode(codesty['encoding'])
        # with open('1.html','a',encoding='utf-8') as fff:
        #     fff.write(rep)
        html = etree.HTML(rep)
        ipaddr = html.xpath(ipa)
        cityaddr = html.xpath(city)
        currentdomain = html.xpath(currdomain)
        text = html.xpath(x1)

        if text:
            pages = (int(text[0]) // 20) + 1
            if pages > MAXPAGE:
                pz_result['city'] = cityaddr[0]
                pz_result['ipaddr'] = ipaddr[0]
                pz_result['pz_number'] = '共有%s个旁站' % text[0]
                pz_result['pz_domains'] = []
                result_report['pz'] = pz_result
                return result_report
            pz_result['city'] = cityaddr[0]
            pz_result['ipaddr'] = ipaddr[0]
            pz_result['pz_number'] = '共有%s个旁站' % text[0]
            x2 = '/html/body/div[4]/div[3]/table/tbody/tr[*]/td[2]/a/text()'
            pz = html.xpath(x2)
            if pz:
                for i in pz:
                    if i not in pz_result['pz_domains']:
                        pz_result['pz_domains'].append(i)
            # print(pages)
            if pages > 1:
                for i in range(2, pages + 1):
                    time.sleep(0.3)
                    search_u = search_url + str(i) + '/'
                    r3 = requests.get(search_u, headers=PANGZHAN_HEADERS, verify=VERIFY)
                    x3 = '/html/body/div[4]/div[3]/table/tbody/tr[*]/td[2]/a/text()'
                    codesty = chardet.detect(r3.content)
                    rep3 = r3.content.decode(codesty['encoding'])
                    html3 = etree.HTML(rep3)
                    text3 = html3.xpath(x3)
                    if text3:
                        for j in text3:
                            if i not in pz_result['pz_domains']:
                                pz_result['pz_domains'].append(j)
            result_report['pz'] = pz_result
            return result_report
        else:
            # pz_result['statu'] = '你查询的域名可能没有旁站哦或者解析出现异常'
            result_report['pz'] = pz_result
            return result_report
    except Exception as e:
        print(e)
        # pz_result['statu'] = '查询出现异常 %s' % e
        result_report['pz'] = pz_result
        return result_report


if __name__ == '__main__':
    print(verify('www.xyaz.cn', RESULT_REPORT))
