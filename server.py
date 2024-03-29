from flask import Flask, render_template, request, make_response, jsonify, url_for, redirect
from flask_cors import *
from HDUCal.schedule2ics import Schedule2ICS
from HDUCal.schedule2json import Schedule2JSON
from HDUCal.gain_schedule import GainSchedule
import os
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/schedule', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/schedule/ics', methods=['POST'])
def icsschedule():
    account = request.form['account']
    password = request.form['password']
    semester_start = request.form['date']
    # print(semester_start)
    year = '2020-2021'
    term = '1'
    raw_schedule = GainSchedule(account, password).run()
    result = Schedule2ICS(raw_schedule, 1).run(semester_start)
    response = make_response(result)
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = "attachment; filename=\"{}.ics\"".format(account)
    return response

@app.route('/schedule/json', methods=['GET'])
def jsonschedule():
    account = request.args.get('xh')
    password = request.args.get('pwd')
    save = (request.args.get('save') if request.args.get('save') != None else 'false')
    year = request.args.get('year')
    term = request.args.get('term')
    if year == None and term == None:
        year = '2020-2021'
        term = '2'
    if account == None or password == None:
        result = {
            "status": "error",
            "msg": "please input your account or password"
        }
        return make_response(jsonify(result))
    else:
        raw_schedule = GainSchedule(account, password, year, term).run()
        result = Schedule2JSON(account, raw_schedule).run(save)
        if isinstance(result, bool) and not result:
            return {"status": False, "msg": "登录失败，学号或密码出错"}
        else:
            if save == 'true':
                # 跳转到保存地址
                print(result)
                return redirect('/schedule/json/'+result)
            else:
                # 直接返回 json 数据
                return make_response(jsonify(result))

@app.route('/schedule/json/<name>')
def jsonscheduleapi(name):
    with open('data/' + name + '.json', 'r', encoding='utf8') as f:
        result = json.load(f)
        return make_response(jsonify(result))


if __name__ == "__main__":
    port = (os.environ['HDUCPORT'] if 'HDUCPORT' in os.environ else 3000)
    isdebug = (os.environ['HDUCDEBUG'] if 'HDUCDEBUG' in os.environ else True)
    app.run(debug=isdebug, host='0.0.0.0', port=port)
