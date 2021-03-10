# HDUCalenderGenerator
[![build](https://github.com/WingLim/HDUCalenderGenerator/actions/workflows/build.yaml/badge.svg)](https://github.com/WingLim/HDUCalenderGenerator/actions/workflows/build.yaml)
[![Docker Pulls](https://img.shields.io/docker/pulls/winglim/hducalgen?logo=docker)](https://hub.docker.com/repository/docker/winglim/hducalgen)
[![Github Package](https://img.shields.io/static/v1?label=WingLim&message=Github%20Package&color=blue&logo=github)](https://github.com/users/WingLim/packages/container/package/hducalgen)

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
semester_start = date(2021, 3, 1)
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

## 使用在线服务
https://api.limxw.com/schedule

## 使用 API
### 请求
```
GET https://api.limxw.com/schedule/json?xh={$学号}&pwd={$密码}&save={$bool}
```
### 参数说明

| 参数名 | 默认值 | 类型   | 说明                       |
| ------ | ------ | ------ | -------------------------- |
| xh     | -      | string | 登录数字杭电的学号         |
| pwd    | -      | string | 登录数字杭电的密码         |
| save   | 0      | bool   | 是否将课程信息保存在服务器 |

PS：即使选择保存，也不保证数据的可持续性，因为本来是拿来给自己用。

PS：如果密码中含 `+` 请转义成 `%2B`

### 返回

```
[
	{
		"title": "计算机网络（甲）", 
		"timeinfo": "周一第1,2节{第1-16周}", 				
		"teacher": "徐明", 
		"location": "第7教研楼北110"
	},
	...
]
```

### 样例

```
GET https://api.limxw.com/schedule/json?xh=18011111&pwd=123456
```






## 搭建 API 服务

### 使用 Docker 搭建

```bash
$ docker pull winglim/hducalgen
$ docker run -itd \
	--name hducalgen 
	-p 3000:3000 
	winglim/hducalgen
```

#### Docker 可选环境变量

| 名词           | 默认值    | 说明                      |
| -------------- | --------- | ------------------------- |
| HDUCPORT       | 3000      | 服务开启的端口            |
| HDUCDEBUG      | True      | Flask 是否开启 debug 模式 |
| SEMESTER_START | 2021-3-01 | 学期开始日期              |

注：`SEMESTER_START` 要参照默认值格式 `YYYY-M-DD`

### 服务器上搭建

> 同本地使用前两步

注意：`info.py` 中填写 `semester_start` 并留空 `account` 和 `password`

### 开启服务
```bash
$ python server.py
```

服务将在 `domain.com:3000/schedule` 开启，监听 `3000` 端口
