from django.shortcuts import render, HttpResponse, redirect
from urllib.parse import urlparse
from django.views.decorators.csrf import csrf_exempt
from lib.utils.parseip import get_ip
from lib.utils.allinfo import get_all_info
from lib.common.urlhandler import slashlessURL


# Create your views here.
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
        result = get_all_info(rawdomain, searchdomain)
        return render(request, 't00ls/integratedquery.html', {'result': result})
    return render(request, 't00ls/integratedquery.html')
