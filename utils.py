import base64
import re
import rsa
import json
import datetime
import time
import traceback

from ui import UI


log = UI.console.log

def encryptPass(password):
    "使用RSA加密密码"
    # 2021.04.17 更新密码加密
    key_str = '''-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OL
    OU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plW
    f5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSR
    wTBNePOk1H+LRQokgQIDAQAB
    -----END PUBLIC KEY-----'''
    pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(key_str.encode('utf-8'))
    crypto = base64.b64encode(rsa.encrypt(
        password.encode('utf-8'), pub_key)).decode()
    return crypto

def extract_js_var(soup, js_var) -> json:
    "从html的<script>标签中获取js的变量,转化为字符串或JSON返回\n"\
        "soup:待识别的网页soup对象;\n"\
        "js_var:待识别的js变量名,若匹配到返回以js_var为根的json,若无法匹配返回None"
    scripts = soup.find_all('script', string=re.compile(js_var, re.DOTALL))
    for script in scripts:
        # 使用正则表达式匹配赋值运算
        # e.g.g     var sessionId = xxxxxx;
        regex = rf'var\s+{js_var}\s+=\s+(.*);'
        if json_str := re.search(regex, script.string):
            return json.loads(json_str.group(1))

def get_days_after_today(n=0):
    "date format = YYYY-MM-DD"
    the_day = datetime.datetime.now() + datetime.timedelta(days=n)
    t = the_day.strftime('%Y-%m-%d')
    return t

def threadProtector(threadFunc):
    def wrapper():
        while True:
            try:
                threadFunc()
            except Exception as e:
                log('[red]发生错误')
                log(traceback.print_exc())
            else:
                log('[red]线程正常退出,线程设计存在问题')
            log(f"[red]重新启动线程{threadFunc.__name__}")
            time.sleep(1)
    return wrapper