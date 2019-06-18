# coding:utf-8
import socket
from lib.utils.isp import getIpInfo

def getIP(searchdomain):
    """
    返回一个三元组
    :param domain: www.tumanduo.com
    :return: (hostname,aliaslist,ipaddrlist)
    """
    try:
        result = socket.gethostbyname_ex(searchdomain)
        # print(result)
        if result:
            dhostname, daliaslist, dipaddrlist = result

            if len(dipaddrlist) == 1:
                ipInfo = getIpInfo(dipaddrlist)
            else:
                ipInfo = dipaddrlist
            if len(daliaslist) >= 1:
                return {'dhostname': dhostname, 'daliaslist': daliaslist, 'dipaddrlist': ipInfo}
            else:
                return {'dhostname': dhostname, 'daliaslist': ['None'], 'dipaddrlist': dipaddrlist}
    except Exception as e:
        print(e)
        return '解析IP失败'


if __name__ == '__main__':
    print(getIP('www.baidu.com'))
    print(getIP('www.tumanduo.com'))
    print(getIP('m.soudongman.com'))
    # print(getIP('www.jzqlz.gov.cn'))
    # print(getIP('www.baidu.com'))
    # print(get_ip('www.yundun.com'))
    # print(get_ip('www.cricchina.com'))
    # print(get_ip('www.legaldaily.com.cn'))
    # print(get_ip('www.jxnyc.net'))
    # print(get_ip('www.qzhxw.com'))
    # print(get_ip('www.shamolang.com'))
    # print(get_ip('www.cityzx.com'))
    # print(get_ip('www.kao8.cc'))
    # print(get_ip('www.biqgew.com'))
    # print(get_ip('www.jianjie8.com'))
    # print(get_ip('www.xuecheyi.com'))
    # print(get_ip('www.tumanduo.com'))
