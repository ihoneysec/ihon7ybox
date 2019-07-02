import threading
import os
import time
import datetime
from urllib3 import disable_warnings
import hashlib
import importlib
import queue
from importlib import util
from importlib.abc import Loader
from requests.models import Request
from requests.sessions import Session
from requests.sessions import merge_setting, merge_cookies
from requests.cookies import RequestsCookieJar
from requests.utils import get_encodings_from_content

disable_warnings()
PATHS_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../")
PATHS_POCS = os.path.join(PATHS_ROOT, "pocs")
PATHS_OUTPUT = os.path.join(PATHS_ROOT, "output")
WORKER = queue.Queue()
POCS = []
global RESULT_REPORT
RESULT_REPORT = {}

CONF = {
    "url": [],
    "poc": [],
    "thread_num": 4,
    "requests": {
        "timeout": 10,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        }
    }
}


def session_request(self, method, url,
                    params=None, data=None, headers=None, cookies=None, files=None, auth=None,
                    timeout=None,
                    allow_redirects=True, proxies=None, hooks=None, stream=None, verify=False, cert=None, json=None):
    # Create the Request.
    conf = CONF.get("requests", {})
    if timeout is None and "timeout" in conf:
        timeout = conf["timeout"]
    merged_cookies = merge_cookies(merge_cookies(RequestsCookieJar(), self.cookies),
                                   cookies or (conf.cookie if 'cookie' in conf else None))

    req = Request(
        method=method.upper(),
        url=url,
        headers=merge_setting(headers, conf["headers"] if 'headers' in conf else {}),
        files=files,
        data=data or {},
        json=json,
        params=params or {},
        auth=auth,
        cookies=merged_cookies,
        hooks=hooks,
    )
    prep = self.prepare_request(req)

    proxies = proxies or (conf["proxies"] if 'proxies' in conf else {})

    settings = self.merge_environment_settings(
        prep.url, proxies, stream, verify, cert
    )

    # Send the request.
    send_kwargs = {
        'timeout': timeout,
        'allow_redirects': allow_redirects,
    }
    send_kwargs.update(settings)
    resp = self.send(prep, **send_kwargs)

    if resp.encoding == 'ISO-8859-1':
        encodings = get_encodings_from_content(resp.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = resp.apparent_encoding

        resp.encoding = encoding

    return resp


def patch_session():
    Session.request = session_request


def get_md5(value):
    if isinstance(value, str):
        value = value.encode(encoding='UTF-8')
    return hashlib.md5(value).hexdigest()


def load_string_to_module(code_string, fullname=None):
    try:
        module_name = 'pocs_{0}'.format(get_md5(code_string)) if fullname is None else fullname
        file_path = 'airpoc://{0}'.format(module_name)
        poc_loader = PocLoader(module_name, file_path)
        poc_loader.set_data(code_string)

        spec = importlib.util.spec_from_file_location(module_name, file_path, loader=poc_loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    except ImportError:
        error_msg = "load module '{0}' failed!".format(fullname)
        print(error_msg)
        raise


class PocLoader(Loader):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path
        self.data = None

    def set_data(self, data):
        self.data = data

    def get_filename(self, fullname):
        return self.path

    def get_data(self, filename):
        if filename.startswith('airpoc://') and self.data:
            data = self.data
        else:
            with open(filename, encoding='utf-8') as f:
                data = f.read()
        return data

    def exec_module(self, module):
        filename = self.get_filename(self.fullname)
        poc_code = self.get_data(filename)
        obj = compile(poc_code, filename, 'exec', dont_inherit=True, optimize=-1)
        exec(obj, module.__dict__)


def init(config: dict):
    # print("[*] target:{}".format(config["url"]))
    patch_session()
    # 加载poc，首先遍历出路径
    _pocs = []
    for root, dirs, files in os.walk(PATHS_POCS):
        files = filter(lambda x: not x.startswith("__") and x.endswith(".py") and x not in config.get("poc", []),
                       files)  # 过滤掉__init__.py文件以及指定poc文件
        _pocs.extend(map(lambda x: os.path.join(root, x), files))

    # 根据路径加载PoC
    for poc in _pocs:
        with open(poc, 'r', encoding='utf-8') as f:
            model = load_string_to_module(f.read())
            POCS.append(model)


def exception_handled_function(thread_function, args=()):
    try:
        thread_function(*args)
    except KeyboardInterrupt:
        raise
    except Exception as ex:
        print("thread {0}: {1}".format(threading.currentThread().getName(), str(ex)))


def run_threads(num_threads, thread_function, args: tuple = ()):
    threads = []

    # Start the threads
    for num_threads in range(num_threads):
        thread = threading.Thread(target=exception_handled_function, name=str(num_threads),
                                  args=(thread_function, args))
        thread.setDaemon(True)
        try:
            thread.start()
        except Exception as ex:
            err_msg = "error occurred while starting new thread ('{0}')".format(str(ex))
            print(err_msg)
            break

        threads.append(thread)

    # And wait for them to all finish
    alive = True
    while alive:
        alive = False
        for thread in threads:
            if thread.isAlive():
                alive = True
                time.sleep(0.1)


def worker():
    if not WORKER.empty():
        arg, poc = WORKER.get()
        try:
            ret = poc.verify(arg, RESULT_REPORT)
        except Exception as e:
            ret = None
            print(e)
        if ret:
            pass
            # print(ret)


def start():
    # print("[*] started at {0}".format(time.strftime("%X")))
    url_list = CONF.get("url", [])

    # 生产
    for arg in url_list:
        for poc in POCS:
            WORKER.put((arg, poc))

    # 消费
    run_threads(CONF.get("thread_num", 10), worker)


def end():
    print("[*] shutting down at {0}".format(time.strftime("%X")))


def main(url):
    RESULT_REPORT = {'rawdomain': '',
                     'parse_ip': {
                         'dhostname': '',
                         'daliaslist': [],
                         'dipaddrlist': []
                     },
                     'cdn_waf': ['未检测到CDN或WAF'],
                     'raw_response': ['源站响应头获取异常'],
                     'pz': {
                         'city': '',
                         'ipaddr': '',
                         'pz_number': '',
                         'pz_domains': []
                     }
                     }
    CONF["url"] = url
    init(CONF)
    start()
    # print(RESULT_REPORT)
    end()


if __name__ == "__main__":
    main(['www.shaipu.com'])
    print(RESULT_REPORT)
