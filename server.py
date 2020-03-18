from flask import Flask, render_template, request, make_response, jsonify, url_for, redirect
from HDUCal.hdu_ics import Schedule2ICS
import os
app = Flask(__name__, static_url_path='/schedule')

@app.route('/schedule', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/schedule/ics', methods=['POST'])
def ics():
    account = request.form['account']
    password = request.form['password']
    semester_start = request.form['date']
    # print(semester_start)
    spider = Schedule2ICS(account, password, 1)
    result = spider.run(semester_start)
    response = make_response(result)
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = "attachment; filename=\"{}.ics\"".format(account)
    return response

@app.route('/schedule/json', methods=['GET'])
def json():
    account = request.args.get('xh')
    password = request.args.get('pwd')
    save = request.args.get('save')
    semester_start = request.args.get('date')
    if account == None or password == None:
        result = {"status": "error", "msg": "please input your account or password"}
        return make_response(jsonify(result))
    else:
        spider = Schedule2ICS(account, password, 1)
        result = spider.run(semester_start, 'json', save)
        if save:
            # 跳转到保存地址
            return redirect(url_for('static', filename = account + '.json'))
        else:
            # 直接返回 json 数据
            return make_response(jsonify(result))

if __name__ == "__main__":
    port = (os.environ['HDUCPORT'] if 'HDUCPORT' in os.environ else 3000)
    isdebug = (os.environ['HDUCDEBUG'] if 'HDUCDEBUG' in os.environ else True)
    app.run(debug=isdebug, host='0.0.0.0', port=port)