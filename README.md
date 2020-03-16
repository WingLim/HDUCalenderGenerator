# HDUCalenderGenerator
Generate HDU schedule icalendar

## 本地使用

### 下载并安装依赖
```bash
$ git clone https://github.com/WingLim/HDUCalenderGenerator.git
$ cd HDUCalenderGenerator
$ pip install -r requirements.txt
```

### 配置
将 `info.example.py` 复制一份到 `info.py`
修改 `info.py` 内容
```python
from datetime import date

# 学期开始时间
semester_start = date(2020,2,24)
# 学号
account = ""
# 密码
password = ""
```

### 生成 .ics
程序会输出 `output.ics` 到根目录
```bash
$ python hdu_ics.py
```

## 使用 API
在对应部分填入账号和密码，该 API 不会记录你的个人信息，如果注意隐私，则自行搭建
https://api.limxw.com/ics/{account}/{password}
