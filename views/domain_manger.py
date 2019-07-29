#!/usr/bin/env python3
# -*- coding=UTF-8 -*-
'''
@Description: 站点管理相关代码
@Author: bayonet
@Github: https://github.com/hyll8882019
@Date: 2019-07-30 19:43:59
@LastEditors: bayonet
@LastEditTime: 2019-07-30 20:24:25
'''
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, render_template, request

from config import *
from public.helper import *
from views.login import login_check

domain = Blueprint('domain', __name__)


@domain.route('/show_domain_list', methods=['GET', ])
@login_check
def show_domain_list():
    current_page = int(request.args.get('page', '1'))

    conn = get_connect()
    db_domain = conn.domain_manager.db_domain
    max_show_num = current_page * MAX_SHOW_NUMBER
    min_show_num = max_show_num - MAX_SHOW_NUMBER
    data = db_domain.find().skip(min_show_num).limit(MAX_SHOW_NUMBER)
    t = db_domain.count_documents({})
    page, max_page = page_format(current_page, t, MAX_SHOW_NUMBER)
    conn.close()
    return render_template('show_domain_list.html', data=data, page=page, current_page=current_page, max_page=max_page)


@domain.route('/api/add_domain', methods=['POST', ])
@login_check
def add_domain():
    info = {'status': False, 'info': '插入数据库失败'}
    if request.method == 'POST':
        title = request.form['title']  # 网站名称
        url = request.form['url']  # 网站地址
        rank_name = request.form['rankname']  # 备注
        js_jump = request.form['js_jump']  # JS 地址
        tpl_name = request.form['tpl_name']  # 模板名
        dir_prefix = request.form['dir_prefix']  # 目录前缀
        web_server_classe = request.form['webserver_classe']  # Web容器
        error_page = request.form['error_page']  # 404错误页
        no_access = request.form['no_access']  # 地区屏蔽
        spider_rules = request.form['spider_rules'].split()  # 放行蜘蛛
        add_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 添加日期
        conn = get_connect()
        db_domain = conn.domain_manager.db_domain

        # 自动添加到链轮库
        rules = ['/hot<随机字符>/', '/hot<随机字符>.html',
                 '/app<随机字符>/', '/app<随机字符>.html']  # 默认路由规则
        hit = 2
        add_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 添加日期
        pool_link = conn.domain_manager.pool_link

        if pool_link.find_one({'_id': url}) is None:
            result = pool_link.insert_one(
                {'_id': url, 'rules': rules, 'hit': hit, 'add_time': add_time})

        if db_domain.find_one({'_id': url}) is None:
            result = db_domain.insert_one(
                {'_id': url, 'title': title, 'rankname': rank_name, 'js_jump': js_jump, 'tpl_name': tpl_name,
                 'dir_prefix': dir_prefix, 'webserver_classe': web_server_classe, 'error_page': error_page,
                 'no_access': no_access, 'add_time': add_time, 'baidu_token': '', 'spider_rules': spider_rules})
            info['status'] = True
            info['info'] = '添加成功'
        else:
            info['status'] = False
            info['info'] = '域名已经存在'
        conn.close()
    return jsonify(info)


@domain.route('/api/edit_domain', methods=['POST', ])
@login_check
def edit_domain():
    info = {'status': False, 'info': ''}
    if request.method == 'POST':
        conn = get_connect()
        db_domain = conn.domain_manager.db_domain
        domain = db_domain.find_one({'_id': request.form['sid']})

        if domain is None:
            info['info'] = '站点不存在'
            return jsonify(info)

        domain['js_jump'] = request.form['js_jump']
        domain['rankname'] = request.form['rankname']
        domain['dir_prefix'] = request.form['dir_prefix']
        domain['tpl_name'] = request.form['tpl_name']
        domain['no_access'] = request.form['no_access']
        domain['error_page'] = request.form['error_page']
        domain['webserver_classe'] = request.form['webserver_classe']
        domain['baidu_token'] = request.form['baidu_token']
        domain['spider_rules'] = request.form['spider_rules'].split()  # 放行蜘蛛
        db_domain.update({'_id': request.form['sid']}, domain)
        info['info'] = '修改成功'
        info['status'] = True
        return jsonify(info)

    info['info'] = '异常请求'
    return jsonify(info)


@domain.route('/api/del_domian', methods=['POST', ])
@login_check
def del_domain():
    info = {'status': False, 'info': ''}
    if request.method == 'POST':
        conn = get_connect()
        db_domain = conn.domain_manager.db_domain
        db_domain.delete_one({'_id': request.form['sid']})
        info['info'] = '删除成功'
        info['status'] = True
        return jsonify(info)

    info['info'] = '异常请求'
    return jsonify(info)


@domain.route('/api/find_domain', methods=['POST', ])
@login_check
def find_domain():
    info = {'status': False, 'info': '站点不存在', 'data': None}
    if request.method == 'POST':
        try:
            sid = request.form['sid']
        except KeyError:
            return jsonify(info)
        conn = get_connect()
        db_domain = conn.domain_manager.db_domain
        info['data'] = db_domain.find_one({'_id': sid})
        info['status'] = True
        info['info'] = ''
        conn.close()
        return jsonify(info)
    info['info'] = '异常请求'
    return jsonify(info)
