import re
from lxml import etree
from lxml.html import tostring
from html.parser import unescape
from HDUCal.login_cas import LoginCAS
from HDUCal.utils import convert_arr


class GainSchedule:
    def __init__(self, stu_account, stu_password, year=None, term=None):
        self.account = stu_account
        self.password = stu_password
        self.year = year
        self.term = term
        self.cas = LoginCAS(stu_account, stu_password)
        self.url = "http://jxgl.hdu.edu.cn/"
        self.base_data = {
            '__EVENTTARGET': 'xnd',
            '__VIEWSTATE': '',
            '__EVENTVALIDATION': '',
            'xnd': '',
            'xqd': ''
        }
        self.headers = {
            'Referer': self.url + self.cas.schedule_url,
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16'
        }

    def export_schedule(self, response):
        selector = etree.HTML(response.content.decode('gb2312'))
        table = selector.xpath("//*[@id='Table1']")[0]
        raw_schedule = []
        tds = table.xpath("//td")
        course_pattern = re.compile(r'<td[^>]*>(.*)</td>')

        for td in tds:
            # 将 Element 对象转换成 string 字符串
            raw = unescape(tostring(td).decode())
            # 用正则匹配获取 <td></td> 标签中的课程信息
            reg = re.search(course_pattern, raw)
            # 不存在则跳过
            if reg == None:
                continue
            # 存在则以 <br> 为分割符，分割成数组
            arr = reg.group(1).split('<br>')
            if len(arr) < 4:
                continue
            elif len(arr) == 9:
                raw_schedule.append(convert_arr(arr[:4]))
                raw_schedule.append(convert_arr(arr[5:]))
                continue
            raw_schedule.append(convert_arr(arr))
        #print(raw_schedule)
        return raw_schedule

    def set_base_data(self, response):
        selector = etree.HTML(response.content)
        viewstate = selector.xpath("//*[@id='__VIEWSTATE']/@value")[0]
        eventvalidation = selector.xpath("//*[@id='__EVENTVALIDATION']/@value")[0]
        self.base_data['__VIEWSTATE'] = viewstate
        self.base_data['__EVENTVALIDATION'] = eventvalidation
        self.base_data['xnd'] = self.year
        self.base_data['xqd'] = self.term

    def run(self):
        islogin = self.cas.login()
        if not islogin:
            return islogin
        else:
            self.cas.headers['Referer'] = self.url + 'xs_main.aspx?xh=' + self.account
            response = self.cas.s.get(self.url + self.cas.schedule_url, headers=self.cas.headers)
            if self.year != None and self.term != None:
                self.set_base_data(response)
                response = self.cas.s.post(self.url + self.cas.schedule_url, data=self.base_data, headers=self.headers)
            return self.export_schedule(response)
