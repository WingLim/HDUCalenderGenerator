import login_cas as lg
import re
import pytz
import icalendar
from lxml import etree
from lxml.html import tostring
from datetime import datetime, time
from html.parser import HTMLParser
from uuid import uuid1
from dateutil.relativedelta import relativedelta
from info import *


class Schedule2ICS:
    def __init__(self, stu_number, stu_password):
        self.number = stu_number
        self.password = stu_password
        self.login = lg.LoginCAS(stu_number, stu_password)
        self.url = "http://jxgl.hdu.edu.cn/"
        self.pattern = re.compile(r'<td[^>]*>(.*)</td>')
        self.dirt_week = {
            1: time(8,5),
            2: time(8,55),
            3: time(10,0),
            4: time(10,50),
            5: time(11,40),
            6: time(13,30),
            7: time(14,20),
            8: time(15,15),
            9: time(16,5),
            10: time(18,30),
            11: time(19,20),
            12: time(20,10)
        }
    
    def parseWeek(self, timeinfo):
        week_pattern = re.compile(r'{[^}]+}')
        data = {
            'from': 0,
            'to': 0,
            'flag': 1
        }
        info = re.search(week_pattern, timeinfo).group()
        single = re.search('单周', info)
        double = re.search('双周', info)
        if single != None:
            data['flag'] = 2
        elif double != None:
            data['flag'] = 2
        dat = re.findall(r'(\d+)', info)
        if dat and len(dat) >= 2:
            data['from'] = int(dat[0])
            data['to'] = int(dat [1])
        return data

    def parseDay(self, timeinfo):
        word = timeinfo[1]
        weekday = {
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "日": 7,
        }
        return weekday[word]
    
    def parseTime(self, timeinfo):
        
        result = []
        timeinfo = timeinfo.split('{')[0]
        dat = re.findall(r'(\d+)', timeinfo)
        for d in dat:
            result.append(course_start[int(d)])
        return result

    def exportCourse(self, response):
        """导出课程信息
        Args:
            response: 请求后返回的响应
        Returns:
            包含所有课程信息字典的数组
            example:
            [
                {
                    'location': '第7教研楼北110', 
                    'name': '计算机网络（甲）', 
                    'teacher': '徐明', 
                    'timeinfo': '周一第1,2节{第1-16周}'
                
                },
                {
                    ...
                }
            ]

        """
        selector = etree.HTML(response.content)
        table = selector.xpath("//*[@id='Table1']")[0]
        raw_courses = []
        tds = table.xpath("//td")
        # 将课程信息数组转换为字典
        def convertArr(arr):
            key = ['name', 'timeinfo', 'teacher', 'location']
            return dict(zip(key, arr))

        for td in tds:
            # 将 Element 对象转换成 string 字符串
            raw = HTMLParser().unescape(tostring(td).decode())
            # 用正则匹配获取 <td></td> 标签中的课程信息
            reg = re.search(self.pattern, raw)
            # 不存在则跳过
            if reg == None:
                continue
            # 存在则以 <br> 为分割符，分割成数组
            arr = reg.group(1).split('<br>')
            if len(arr) < 4:
                continue
            elif len(arr) == 9:
                raw_courses.append(convertArr(arr[:4]))
                raw_courses.append(convertArr(arr[5:]))
                continue
            raw_courses.append(convertArr(arr))
        # print(raw_courses)
        return raw_courses
    
    def cookCourse(self, raw_courses):
        calt = icalendar.Calendar()
        calt['version'] = '2.0'
        for one in raw_courses:
            week = self.parseWeek(one['timeinfo'])
            week_start = week['from']
            week_end = week['to']
            interval = week['flag']
            count = (week_end - week_start + 1) if interval == 1 else (((week_end - week_start) / 2) + 1)
            course_weekday = self.parseDay(one['timeinfo'])
            
            timeinfo = one['timeinfo'].split('{')[0]
            course_period_regrx = re.compile(r'(\d+)')  # 编译正则
            course_period_list = course_period_regrx.findall(timeinfo, 1)  # 得到一个课时的list
            course_period_num = len(course_period_list)  # 一共几节课
            course_period_start = int(course_period_list[0])  # 第一节课的课时号
            course_period_end = int(course_period_list[course_period_num - 1])  # 最后一节课的课时号
            
            lesson_time = relativedelta(minutes=45)
            dt_date = semester_start + relativedelta(weeks=(week_start - 1)) + relativedelta(
            days=(course_weekday - 1))  # 课程日期

            dtstart_time = self.dirt_week[course_period_start]  # 上课时间
            dtend_time = self.dirt_week[course_period_end]  # 最后一节小课上课时间
            
            dtstart_datetime = datetime.combine(dt_date, dtstart_time, tzinfo=pytz.timezone("Asia/Shanghai"))  # 上课日期时间
            dtend_datetime = datetime.combine(dt_date, dtend_time, tzinfo=pytz.timezone("Asia/Shanghai"))  # 下课日期时间
            dtend_datetime += lesson_time

            event = icalendar.Event()
            event.add('summary', one['name']) # 标题/课程名
            event.add('uid', str(uuid1()) + '@HDU') # UUID
            event.add('dtstamp', datetime.now()) # 创建时间
            event.add('location', one['location'])
            event.add('description',
                  '第{}-{}节\r\n教师： {}\r\n教室: {}'.format(course_period_start, course_period_end, one['teacher'],
                                                       one['location']))  # 教师名称
            event.add('dtstart', dtstart_datetime)
            event.add('dtend', dtend_datetime)
            event.add('rrule', {'freq': 'weekly', 'interval': interval, 'count': count})

            calt.add_component(event)
        with open('output.ics', 'w+', encoding='utf-8', newline='') as file:
            # file.write(calt.to_ical().decode('utf-8'))
            file.write(calt.to_ical().decode('utf-8'.replace('\r\n', '\n')).strip())


    def run(self):
        while not self.login.login():
            continue
        self.login.headers['Referer'] = self.url + 'xs_main.aspx?xh=' + self.number
        response = self.login.s.get(self.url + self.login.schedule_url, headers=self.login.headers)
        # print(response.text)
        raw_courses = self.exportCourse(response)
        courses = self.cookCourse(raw_courses)
        

if __name__ == "__main__":
    spider = Schedule2ICS(account, password)
    spider.run()