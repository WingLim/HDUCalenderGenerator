from flask import Flask, render_template, request, make_response
import hdu_ics
app = Flask(__name__)

@app.route('/ics', methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        spider = hdu_ics.Schedule2ICS(account, password, 1)
        result = spider.run()
        response = make_response(result)
        response.headers['Content-Type'] = 'text/calendar'
        response.headers['Content-Disposition'] = "attachment; filename=\"{}.ics\"".format(account)
        return response
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9898)