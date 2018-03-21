from flask import Blueprint
# 在蓝本中实现程序功能,实例化一个蓝本类对象创建蓝本
main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)