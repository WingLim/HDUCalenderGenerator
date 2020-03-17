from flask import Flask, render_template, request, make_response, jsonify, url_for, redirect
import hdu_ics
import os
app = Flask(__name__, static_url_path='/schdule')

@app.route('/schdule', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/schdule/ics', methods=['POST'])
def ics():
    account = request.form['account']
    password = request.form['password']
    semester_start = request.form['date']
    print(semester_start)
    spider = hdu_ics.Schedule2ICS(account, password, 1)
    result = spider.run(semester_start)
    response = make_response(result)
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = "attachment; filename=\"{}.ics\"".format(account)
    return response

@app.route('/schdule/json', methods=['GET'])
def json():
    account = request.args.get('account')
    password = request.args.get('password')
    save = request.args.get('save')
    semester_start = request.args.get('date')
    spider = hdu_ics.Schedule2ICS(account, password, 1)
    result = spider.run('json', save, semester_start)
    if save:
        return redirect(url_for('static', filename = account + '.json'))
    else:
        return make_response(jsonify(result))

    

if __name__ == "__main__":
    port = (os.environ['PORT'] if 'PORT' in os.environ else 3000)
    isdebug = (os.environ['DEBUG'] if 'DEBUG' in os.environ else True)
    app.run(debug=isdebug, host='0.0.0.0', port=port)