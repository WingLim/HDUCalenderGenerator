import pytz
import icalendar
from datetime import datetime, date
from uuid import uuid1
from dateutil.relativedelta import relativedelta
from HDUCal import info
from HDUCal.utils import parse_week, parse_time, get_key


class Schedule2ICS:
    def __init__(self, raw_schedule, isserver=0):
        self.raw_schedule = raw_schedule
        # 是否为服务器状态
        self.isserver = isserver
        # 上课时间表

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
            week = parse_week(t)
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
            dtstart_time, dtend_time = parse_time(t)
            
            # 上课日期时间
            dtstart_datetime = datetime.combine(dt_date, dtstart_time, tzinfo=pytz.timezone("Asia/Shanghai"))
            # 下课日期时间
            dtend_datetime = datetime.combine(dt_date, dtend_time, tzinfo=pytz.timezone("Asia/Shanghai"))

            event = icalendar.Event()
            # 标题/课程名
            event.add('summary', one['title'])
            # UUID 作为独立标识
            event.add('uid', str(uuid1()) + '@HDU')
            event.add('dtstamp', datetime.now())
            # 上课地点
            event.add('location', one['location'])
            # 详细信息
            event.add('description',
                  '第{}-{}节\r\n教师： {}\r\n教室: {}'.format(
                      get_key('start', dtstart_time),
                      get_key('end', dtend_time),
                      one['teacher'], one['location']))
            event.add('dtstart', dtstart_datetime)
            event.add('dtend', dtend_datetime)
            event.add('rrule', {'freq': 'weekly', 'interval': interval, 'count': count})

            calt.add_component(event)
        return calt

    def run(self, semester_start=info.semester_start):
        semester_start = self.parse_semester_start(semester_start)
        calt = self.cook_courses(self.raw_schedule, semester_start)
        if not self.isserver:
            with open('output.ics', 'w+', encoding='utf-8', newline='') as file:
                file.write(calt.to_ical().decode('utf-8'.replace('\r\n', '\n')).strip())
        else:
            return calt.to_ical().decode('utf-8'.replace('\r\n', '\n').strip())

if __name__ == "__main__":
    spider = Schedule2ICS(info.account, '777')
    spider.run()