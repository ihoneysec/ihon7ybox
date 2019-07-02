from django.shortcuts import render, HttpResponse, redirect
from urllib.parse import urlparse
from django.views.decorators.csrf import csrf_exempt
from lib.utils.allinfo import get_all_info


def index(request):
    return render(request, 't00ls/index.html')


def integratedquery(request):
    request.encoding = 'utf-8'
    rawdomain = request.POST.get('domain')
    if rawdomain:
        rawdomain = rawdomain.strip()
        searchdomain = rawdomain
        if '://' in searchdomain:  searchdomain = urlparse(searchdomain).netloc
        if '/' in searchdomain: searchdomain = searchdomain.split('/')[0]
        result = get_all_info(searchdomain)
        # result = {'rawdomain': 'www.shaipu.com', 'parse_ip': {'dhostname': 'shaipu.w77.cndns5.com', 'daliaslist': ['www.shaipu.com'], 'dipaddrlist': ['210.16.190.55']}, 'ip_city': 'None', 'pz_number': 'None', 'cdn_waf': ['SDWAF'], 'raw_response': ['HTTP/1.1 200 OK', '\r\nCache-Control: private', '\r\nContent-Type: text/html; charset=utf-8', '\r\nContent-Encoding: gzip', '\r\nVary: Accept-Encoding', '\r\nSet-Cookie: sdwaf-test-item=81a3eb560608060407070104560106515c03020d065107010801010b025306; path=/; HttpOnly', '\r\nX-Powered-By: SDWAF', '\r\nDate: Tue, 02 Jul 2019 17:37:12 GMT', '\r\nContent-Length: 8151']}
        return render(request, 't00ls/integratedquery.html', {'result': result})
    return render(request, 't00ls/integratedquery.html')
