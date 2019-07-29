#!/usr/bin/env python3
# -*- coding=UTF-8 -*-
'''
@Description: 自定义登录函数
@Author: bayonet
@Github: https://github.com/hyll8882019
@Date: 2019-07-30 19:48:59
@LastEditors: bayonet
@LastEditTime: 2019-07-30 20:17:55
'''

from flask import request
from config import PASSWORD

def login_check(func):
    '''
    @description: 登录验证. 只验证Cookies
    '''
    def wrapper(*args, **kwargs):
        ss = request.cookies.get("ss", None)
        if ss is None or ss != PASSWORD:
            return "404"
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
