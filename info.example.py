from datetime import date
import os

if 'SEMESTER_START' in os.environ:
    start = os.environ['SEMESTER_START'].split('-')
    start = list(map(int, start))
    if len(start) == 3:
        semester_start = date(start[0], start[1], start[2])
else:
    # 学期开始时间
    semester_start = date(2020,2,24)

# 学号
account = ""
# 密码
password = ""