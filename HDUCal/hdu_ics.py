import re
import pytz
import icalendar
from lxml import etree
from lxml.html import tostring
from datetime import datetime, time, date
from html.parser import HTMLParser
from uuid import uuid1
from dateutil.relativedelta import relativedelta
from HDUCal.login_cas import LoginCAS
from HDUCal import info


class Schedule2ICS:
    def __init__(self, stu_account, stu_password, isserver=0):
        self.account = stu_account
        self.password = stu_password
        self.cas = LoginCAS(stu_account, stu_password)
        self.url = "http://jxgl.hdu.edu.cn/"
        # 是否为服务器状态
        self.isserver = isserver
        # 上课时间表
        self.dirt_week_start = {
            1: time(8,5),
            3: time(10,0),
            6: time(13,30),
            8: time(15,15),
            10: time(18,30),
            11: time(19,20)
        }
        self.dirt_week_end = {
            2: time(9,40),
            4: time(11,35),
            5: time(12,25),
            7: time(15,5),
            8: time(16,0),
            9: time(16,50),
            11: time(20,5),
            12: time(20,55)
        }
    
    def parse_week(self, timeinfo):
        """解析课程每周信息
        Args:
            timeinfo: 课程的时间信息
        Returns:
            一个字典，包含开始周，结束周以及是否单双周
            flag 为 1 则为每周上课，flag 为 2 则为单/双周上课
            例子:
            {
                'start': 1,
                'end': 16,
                'flag': 1
            }
        """
        week_pattern = re.compile(r'{[^}]+}')
        data = {
            'start': 0,
            'end': 0,
            'flag': 0
        }
        info = re.search(week_pattern, timeinfo).group()
        single = re.search('单周', info)
        double = re.search('双周', info)
        if single != None:
            data['flag'] = 1
        elif double != None:
            data['flag'] = 2
        dat = re.findall(r'(\d+)', info)
        if dat and len(dat) >= 2:
            data['start'] = int(dat[0])
            data['end'] = int(dat [1])
        return data
    
    def parse_time(self, timeinfo):
        course_period_regrx = re.compile(r'(\d+)')
        timeinfo = timeinfo.split('{')[0]
        course_period_list = course_period_regrx.findall(timeinfo, 1)
        # 一共几节课
        course_period_num = len(course_period_list)
        # 第一节课是第几节
        course_period_start = int(course_period_list[0])
        # 最后一节是第几节
        course_period_end = int(course_period_list[course_period_num - 1])
        # 开始上课时间
        dtstart_time = self.dirt_week_start[course_period_start]
        # 最后一节课下课时间
        dtend_time = self.dirt_week_end[course_period_end]
        return dtstart_time, dtend_time

    def parse_day(self, timeinfo):
        """解析课程在星期几上课
        Args:
            timeinfo: 课程的时间信息
        Returns:
            数字，周一到周日分别为 1 到 7
        """
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

    def parse_semester_start(self, semester_start):
        if isinstance(semester_start, str):
            start = semester_start.split('-')
            start = list(map(int, start))
            result = date(start[0], start[1], start[2])
        else:
            result = semester_start
        return result

    def export_course(self, response):
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
        selector = etree.HTML(response.content.decode('gb2312'))
        table = selector.xpath("//*[@id='Table1']")[0]
        raw_courses = []
        tds = table.xpath("//td")
        course_pattern = re.compile(r'<td[^>]*>(.*)</td>')
        # 将课程信息数组转换为字典
        def convertArr(arr):
            key = ['name', 'timeinfo', 'teacher', 'location']
            return dict(zip(key, arr))

        for td in tds:
            # 将 Element 对象转换成 string 字符串
            raw = HTMLParser().unescape(tostring(td).decode())
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
                raw_courses.append(convertArr(arr[:4]))
                raw_courses.append(convertArr(arr[5:]))
                continue
            raw_courses.append(convertArr(arr))
        # print(raw_courses)
        return raw_courses
    
    def get_key(self, type, value):
        if type == 'start':
            d = self.dirt_week_start
        elif type == 'end':
            d = d = self.dirt_week_end
        return [k for k,v in d.items() if v == value]


    def cook_course_json(self, export_courses):
        result = []
        for one in export_courses:
            info = {}
            t = one['timeinfo']
            info['week'] = self.parse_week(t)
            info['weekday'] = t[0,2]
            info['start'], info['end'] = (i.strftime('%H:%M') for i in self.parse_time(t)) 
            one['timeinfo'] = info
            result.append(one)
        return result
             
    
    def cook_courses(self, export_courses, semester_start):
        """处理课程信息为 ical
        将导出后的课程信息转化成 ical 格式
        Args:
            export_courses: 经过处理后导出的课程信息数组
            semester_start: 开始上课的第一天
        Returns:
            icalendar 对象
        """
        calt = icalendar.Calendar()
        calt['version'] = '2.0'
        for one in export_courses:
            t = one['timeinfo']
            week = self.parse_week(t)
            # 课程开始周
            week_start = week['start']
            # 课程结束周
            week_end = week['end']
            # 单双周标记
            interval = week['flag']
            # 本学期该课程上课总数
            count = (week_end - week_start + 1) if interval == 0 else (((week_end - week_start) / 2) + 1)
            course_weekday = self.parse_day(t)
            
            # 课程日期
            dt_date = semester_start + relativedelta(weeks=(week_start - 1)) + relativedelta(
                days=(course_weekday - 1))
            # 开始上课时间
            dtstart_time, dtend_time = self.parse_time(t)
            
            # 上课日期时间
            dtstart_datetime = datetime.combine(dt_date, dtstart_time, tzinfo=pytz.timezone("Asia/Shanghai"))
            # 下课日期时间
            dtend_datetime = datetime.combine(dt_date, dtend_time, tzinfo=pytz.timezone("Asia/Shanghai"))

            event = icalendar.Event()
            # 标题/课程名
            event.add('summary', one['name'])
            # UUID 作为独立标识
            event.add('uid', str(uuid1()) + '@HDU')
            event.add('dtstamp', datetime.now())
            # 上课地点
            event.add('location', one['location'])
            # 详细信息
            event.add('description',
                  '第{}-{}节\r\n教师： {}\r\n教室: {}'.format(
                      self.get_key('start', dtstart_time), 
                      self.get_key('end', dtend_time), 
                      one['teacher'], one['location']))
            event.add('dtstart', dtstart_datetime)
            event.add('dtend', dtend_datetime)
            event.add('rrule', {'freq': 'weekly', 'interval': interval, 'count': count})

            calt.add_component(event)
        return calt

    def run(self, semester_start=info.semester_start, filetype='ics', save='false'):
        # 登录
        islogin = self.cas.login()
        if not islogin:
            return islogin
        else:
            # 跳转到个人课表页面，获取 HTML 内容
            self.cas.headers['Referer'] = self.url + 'xs_main.aspx?xh=' + self.account
            response = self.cas.s.get(self.url + self.cas.schedule_url, headers=self.cas.headers)
            export_courses = self.export_course(response)
            if filetype == 'ics':
                semester_start = self.parse_semester_start(semester_start)
                calt = self.cook_courses(export_courses, semester_start)
                if not self.isserver:
                    with open('output.ics', 'w+', encoding='utf-8', newline='') as file:
                        file.write(calt.to_ical().decode('utf-8'.replace('\r\n', '\n')).strip())
                else:
                    return calt.to_ical().decode('utf-8'.replace('\r\n','\n').strip())
            # json 格式只用于 API 服务
            elif filetype == 'json' and self.isserver:
                result = self.cook_course_json(export_courses)
                if save == 'true':
                    # 如果保存，则写入到 static/学号.json 中
                    account = self.account
                    with open('data/' + account + '.json', 'w+', encoding='utf-8', newline='') as file:
                        file.write(str(result).replace("'",'"'))
                    return account
                else:
                    # 不保存则直接返回 list
                    return result

if __name__ == "__main__":
    spider = Schedule2ICS(info.account, '777')
    spider.run()