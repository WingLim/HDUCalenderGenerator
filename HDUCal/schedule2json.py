from HDUCal.utils import parse_week, parse_time


class Schedule2JSON:
    def __init__(self, stu_account, raw_schedule):
        self.account = stu_account
        self.raw_schedule = raw_schedule

    def cook_schedule_json(self, export_courses):
        result = []
        for one in export_courses:
            info = {}
            t = one['timeinfo']
            info['week'] = parse_week(t)
            info['weekday'] = t[0:2]
            info['start'], info['end'] = (i.strftime('%H:%M') for i in parse_time(t))
            one['timeinfo'] = info
            result.append(one)
        return result

    def run(self, save=False):
        result = self.cook_schedule_json(self.raw_schedule)
        if save == 'true':
            # 如果保存，则写入到 static/学号.json 中
            account = self.account
            with open('data/' + account + '.json', 'w+', encoding='utf-8', newline='') as file:
                file.write(str(result).replace("'", '"'))
            return account
        else:
            # 不保存则直接返回 list
            return result