from flask import Flask,render_template
from flask import request
from flask import make_response
from flask import redirect
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
	# 程序和请求上下文
    # user_agent = request.headers.get('User-Agent')
    # return '<p>Your browser is %s</p>' % user_agent
    # 响应
    # return '<h1>Bad Request</h1>',400
    # 返回cookie
    # resopnse = make_response('<h1>This document carries a cookie!</h1>')
    # resopnse.set_cookie('answer','42')
    # return resopnse
    # 辅助函数
    # return redirect('http://www.example.com')
    # 返回模板渲染的html页面
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    # return '<h1>Hello,%s!</h1>' % name
    # 返回模板渲染的html页面
    return render_template('user.html',name=name)


# 用于处理错误，url中对应的id不存在就返回404
@app.route('/user/<id>')
def get_user(id):
	user = load_user(id)
	if not user:
		abort(404)
	return '<h1>Hello,%s</h1>' %user.name


if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=5000,debug=True)
    manager.run()
