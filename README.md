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
在对应部分填入账号和密码，该 API 不会记录你的个人信息，如果担心泄露隐私，则在本地使用或自行搭建
https://api.limxw.com/ics/{account}/{password}

## 搭建 API 服务

> 同本地使用前两步

注意：`info.py` 中填写 `semester_start` 并留空 `account` 和 `password`

### 开启服务
```bash
$ python server.py
```

服务将在 `domain.com:9898/ics/` 开启，监听 `9898` 端口

端口在 [server.py#L31](https://github.com/WingLim/HDUCalenderGenerator/blob/9dc344cb9416c2bf3f6d271a3c8fea61113cdac9/server.py#L31) 处修改

后缀即 `/ics/` 在 [server.py#L8](https://github.com/WingLim/HDUCalenderGenerator/blob/9dc344cb9416c2bf3f6d271a3c8fea61113cdac9/server.py#L8) 和 [server.py#L16](https://github.com/WingLim/HDUCalenderGenerator/blob/9dc344cb9416c2bf3f6d271a3c8fea61113cdac9/server.py#L16) 处修改
