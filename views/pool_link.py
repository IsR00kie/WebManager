#!/usr/bin/env python3
# -*- coding=UTF-8 -*-
'''
@Description: 轮链管理相关代码
@Author: bayonet
@Github: https://github.com/hyll8882019
@Date: 2019-07-30 19:44:29
@LastEditors: bayonet
@LastEditTime: 2019-07-30 20:24:15
'''
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, render_template, request

from config import *
from public.helper import *
from views.login import login_check
link = Blueprint('link', __name__)


@link.route('/api/show_pool_link')
@login_check
def show_pool_link():
    current_page = int(request.args.get('page', '1'))

    conn = get_connect()
    pool_link = conn.domain_manager.pool_link
    max_show_num = current_page * MAX_SHOW_NUMBER
    min_show_num = max_show_num - MAX_SHOW_NUMBER
    data = pool_link.find().skip(min_show_num).limit(MAX_SHOW_NUMBER)
    t = pool_link.count_documents({})
    page, max_page = page_format(current_page, t, 20)
    return render_template('show_pool_link.html', data=data, page=page, current_page=current_page, max_page=max_page)


@link.route('/api/add_pool_link', methods=['POST', ])
@login_check
def add_pool_link():
    info = {'status': False, 'info': '插入数据库失败'}
    if request.method == 'POST':
        domain = request.form['slink_domain']  # 网站地址
        rules = request.form['slink_rules'].split()  # 路由规则
        hit = request.form['slink_level']  # 权重
        add_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 添加日期

        conn = get_connect()
        db_domain = conn.domain_manager.pool_link
        if db_domain.find_one({'_id': domain}) is None:
            result = db_domain.insert_one(
                {'_id': domain, 'rules': rules, 'hit': hit, 'add_time': add_time})
            info['status'] = True
            info['info'] = '添加成功'
        else:
            info['status'] = False
            info['info'] = '域名已经存在'
        conn.close()
    return jsonify(info)


@link.route('/api/find_pool_link', methods=['POST', ])
@login_check
def find_pool_link():
    info = {'status': False, 'info': '轮链不存在', 'data': None}
    if request.method == 'POST':
        try:
            sid = request.form['sid']
        except KeyError:
            return jsonify(info)
        conn = get_connect()
        db_domain = conn.domain_manager.pool_link
        info['data'] = db_domain.find_one({'_id': sid})
        info['status'] = True
        info['info'] = ''
        conn.close()
        return jsonify(info)

    info['info'] = '异常请求'
    return jsonify(info)


@link.route('/api/edit_pool_link', methods=['POST', ])
@login_check
def edit_pool_link():
    info = {'status': False, 'info': ''}
    if request.method == 'POST':
        conn = get_connect()
        db_domain = conn.domain_manager.pool_link
        domain = db_domain.find_one({'_id': request.form['sid']})

        if domain is None:
            info['info'] = '站点不存在'
            return jsonify(info)

        domain['hit'] = request.form['slink_level']
        domain['rules'] = request.form['slink_rules'].split()

        db_domain.update({'_id': request.form['sid']}, domain)
        info['info'] = '修改成功'
        info['status'] = True
        return jsonify(info)

    info['info'] = '异常请求'
    return jsonify(info)


@link.route('/api/del_pool_link', methods=['POST', ])
@login_check
def del_pool_link():
    info = {'status': False, 'info': ''}
    if request.method == 'POST':
        conn = get_connect()
        db_domain = conn.domain_manager.pool_link
        db_domain.delete_one({'_id': request.form['sid']})
        info['info'] = '删除成功'
        info['status'] = True
        return jsonify(info)

    info['info'] = '异常请求'
    return jsonify(info)
