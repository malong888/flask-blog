#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-3-20 下午6:17
# @Author  : Michael
# @Site    : 
# @File    : decorators.py
# @Software: PyCharm

from functools import wraps
from flask import g
from .errors import forbidden

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			if not g.current_user.can(permission):
				return forbidden('Insufficient permissions')
			return f(*args, **kwargs)
		return decorated_function
	return decorator
