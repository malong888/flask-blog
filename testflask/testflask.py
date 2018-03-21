'''
# coding:utf-8
from flask import Flask,render_template,session,url_for,flash
from flask import request
from flask import make_response
from flask import redirect
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.script import Shell
from flask.ext.migrate import Migrate,MigrateCommand
from flask.ext.mail import Mail
from flask.ext.mail import Message
from threading import Thread



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI']=\
    'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <mlhcc_1314@163.com>'
app.config['FLASKY_ADMIN']= os.environ.get('FLASKY_ADMIN')
# app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')



db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app,db)
mail = Mail(app)






# 定义Role和User模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' %self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' %self.username



# def send_email(to, subject, template, **kwargs):
#     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs)
#     msg.html = render_template(template + '.html', **kwargs)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


# 表单类
class NameForm(Form):
    name = StringField('What is your name?',validators=[Required()])
    submit = SubmitField('Submit')


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.route('/',methods=['GET','POST'])
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
    # 返回模板渲染的html页面,时间信息
    # return render_template('index.html',current_time=datetime.utcnow())
    # 在视图函数中处理表单，不仅渲染表单，还要接收表单中的数据
    # name = None
    # form = NameForm()
    # if form.validate_on_submit():
    #     # 重定向和用户回话
    #     old_name = session.get('name')
    #     if old_name is not None and old_name != form.name.data:
    #         flash('Looks like you have changed your name!')
    #     session['name'] = form.name.data
    #     return redirect(url_for('index'))
    #     # name = form.name.data
    #     # form.name.data = ''
    # return render_template('index.html',form=form,name=session.get('name'))
    # 在视图函数中操作数据库
    # form = NameForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.name.data).first()
    #     if user is None:
    #         user = User(username = form.name.data)
    #         db.session.add(user)
    #         session['known'] = False
    #     else:
    #         session['known'] = True
    #     session['name'] = form.name.data
    #     form.name.data=''
    #     return redirect(url_for('index'))
    # return render_template('index.html',form = form,name = session.get('name'),known = session.get('known',False))

    # 同步发送邮件
    # msg = Message('邮件主题', sender='mlhcc_1314@163.com', recipients=['mlhcc_1314@163.com'])
    # msg.body = '邮件内容'
    # msg.html = "<h1>邮件的html模板<h1> body"
    # with app.app_context():
    #     mail.send(msg)

    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data=''
        return redirect(url_for('index'))
    return render_template('index.html',form = form,name = session.get('name'),known = session.get('known',False))


@app.route('/user/<name>')
def user(name):
    # return '<h1>Hello,%s!</h1>' % name
    # 返回模板渲染的html页面
    return render_template('user.html',name=name)


# 用于处理错误，url中对应的id不存在就返回404
# @app.route('/user/<id>')
# def get_user(id):
# 	user = load_user(id)
# 	if not user:
# 		abort(404)
# 	return '<h1>Hello,%s</h1>' %user.name

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))






if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=5000,debug=True)
    manager.run()
'''