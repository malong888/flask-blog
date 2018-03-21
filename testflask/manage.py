import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

import sys
import click
from flask_migrate import Migrate, upgrade,MigrateCommand
from app import create_app, db
from flask_script import Manager, Shell
from app.models import User, Follow, Role, Permission, Post, Comment

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# 为flask程序添加一个命令行解析器
manager = Manager(app)
migrate = Migrate(app, db)

# 使用程序实例提供的app.route修饰器,把修饰的函数注册为路由
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Follow=Follow, Role=Role,
                Permission=Permission, Post=Post, Comment=Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
def test(coverage):
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@app.cli.command()
@click.option('--length', default=25,
              help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None,
              help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@app.cli.command()
def deploy():
    upgrade()
    Role.insert_roles()
    User.add_self_follows()

# 多文件flask程序基本结构一般有４个顶级文件夹
# flask程序一般保存在名为app的包中
# 和之前一样,migrations文件夹包含数据迁移脚本
# 单元测试编写在tests包中
# venv文件夹包含python虚拟环境
# requirements.txt列出了所有依赖包
# config.py存储配置
# manage.py用于启动程序以及其他的程序任务

# 程序实例用run方法启动flask集成的web服务器
if __name__ == '__main__':
    manager.run()
