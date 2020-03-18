import json
import requests
import re
import info
from datetime import datetime
from lxml import etree
from des import strEnc

# 判断登录状态
def login_status(response):
    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if response.status_code == requests.codes.ok:
        selector = etree.HTML(response.content.decode('gb2312'))
        state = selector.xpath('/html/head/title/text()')[0]
        if state == "正方教务管理系统":
            print("{}: 登录成功".format(now_time))
            return True
        elif state == "HDU统一身份认证系统":
            print("{}: 登录失败".format(now_time))
            return False
    else:
        print(response.status_code)
        print("{}: 登录失败".format(now_time))
        return False

# 获取学生名字
def get_name(response):
    selector = etree.HTML(response.content.decode('gb2312'))
    name = selector.xpath("//*[@id='xhxm']/text()")[0]
    name = name[:-2]
    return name

class LoginCAS:
    def __init__(self, stu_account, stu_password):
        self.account = stu_account
        self.password = stu_password
        self.name = ""
        self.index_url = 'http://cas.hdu.edu.cn/cas/login?service=http://jxgl.hdu.edu.cn/default.aspx'
        self.zf_url = 'http://jxgl.hdu.edu.cn/xs_main.aspx?xh=' + self.account
        self.schedule_url = ""
        self.s = requests.session()
        self.headers = {
            'Referer': self.index_url,
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16'
        }
        self.data = {
            'rsa': '',
            'ul': '',
            'pl': '',
            'lt': '',
            'execution': '',
            '_eventId': "submit"
        }
    
    def get_lt_execution(self):
        response = self.s.get(self.index_url, headers=self.headers)
        selector = etree.HTML(response.content)
        template = selector.xpath("//*[@id='password_template']/text()")[0]
        # print(template)
        lt = re.search('LT-.*-cas',template).group()
        execution = re.search('e[0-9]s[0-9]',template).group()
        return lt, execution
        
    # 计算 rsa
    def caculate_rsa(self):
        total = self.account + self.password + self.data['lt']
        rsa = strEnc(total,"1","2","3")
        return rsa

    # 获取学生个人课表地址
    def get_schedule_url(self, response):
        selector = etree.HTML(response.content)
        schedule_url = selector.xpath("//*[@id='headDiv']/ul/li[6]/ul/li[2]/a/@href")[0]
        return schedule_url
    
    def login(self):
        self.data['lt'], self.data['execution'] = self.get_lt_execution()
        self.data['rsa'] = self.caculate_rsa()
        self.data['ul'] = str(len(self.account))
        self.data['pl'] = str(len(self.password))
        response = self.s.post(self.index_url, headers=self.headers, data=self.data)
        self.headers['Referer'] = response.url
        response = self.s.get(self.zf_url, headers=self.headers)
        self.schedule_url = self.get_schedule_url(response)
        # print(response.content.decode("gb2312"))
        if login_status(response):
            self.name = get_name(response)
            #print(self.name)
            return True
        else:
            return False

if __name__ == "__main__":
    spider = LoginCAS(info.account, info.password)
    spider.login()