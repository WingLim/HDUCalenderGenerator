from datetime import time
import re

dict_week_start = {
    1: time(8, 5),
    2: time(8, 55),
    3: time(10, 0),
    4: time(10, 50),
    5: time(11, 40),
    6: time(13, 30),
    7: time(14, 20),
    8: time(15, 15),
    9: time(16, 5),
    10: time(18, 30),
    11: time(19, 20),
    12: time(20, 10)
}

dict_week_end = {
    1: time(8, 50),
    2: time(9, 40),
    3: time(10, 45),
    4: time(11, 35),
    5: time(12, 25),
    6: time(14, 15),
    7: time(15, 5),
    8: time(16, 0),
    9: time(16, 50),
    10: time(19, 15),
    11: time(20, 5),
    12: time(20, 55)
}


# 将课程信息数组转换为字典
def convert_arr(arr):
    key = ['title', 'timeinfo', 'teacher', 'location']
    return dict(zip(key, arr))


def get_key(type, value):
    if type == 'start':
        d = dict_week_start
    elif type == 'end':
        d = dict_week_end
    return [k for k, v in d.items() if v == value]


def parse_week(timeinfo):
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
        data['end'] = int(dat[1])
    return data


def parse_time(timeinfo):
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
    dtstart_time = dict_week_start[course_period_start]
    # 最后一节课下课时间
    dtend_time = dict_week_end[course_period_end]
    return dtstart_time, dtend_time
