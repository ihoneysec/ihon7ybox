# coding:utf-8


def slashlessURL(url):
    """
    返回网址没有最后斜杠的格式，获取CMS指纹专用
    :param url:
    :return: http://www.t00ls.net
    """
    url = url.strip()
    if '://' not in url:
        url = 'http://' + url
    if url.endswith('/'):
        url = url.rstrip('/')
    return url


def addslashless(url):
    """
    返回网址最后带斜杠的格式，检测CDN/WAF专用
    :param url:
    :return: http://www.t00ls.net/
    """
    url = url.strip()
    if '://' not in url:
        url = 'http://' + url
    if not url.endswith('/'):
        url = url + "/"
    return url
