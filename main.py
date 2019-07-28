#!/usr/bin/env python3
# -*- coding=UTF-8 -*-
'''
@Description: 反代项目管理系统
@Author: bayonet
@Github: https://github.com/hyll8882019
@Date: 2019-07-28 20:37:12
@LastEditors: bayonet
@LastEditTime: 2019-07-28 21:14:51
'''
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import timedelta, datetime
import os
import pymongo
import hashlib
import random
import re

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join('/db', 'cache')


def login_check(func):
    '''
    @description: 登录验证. 只验证Cookies
    '''
    def wrapper(*args, **kwargs):
        ss = request.cookies.get("ss", None)
        if ss is None or ss != 'you password':
            return "404"
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# 自定义公共函数开始

def to_unicode(string):
    '''
    @description: 字符串转Unicode字符串
    @param string: 准备转换的字符串
    @return:  返回转换后的Unicode字符串
    '''
    ret = ''
    for v in string:
        ret = ret + "&#" + str(int(hex(ord(v)), 16))
    return ret


def get_md5(data):
    '''
    @description: 取传入数据的MD5值
    @param data:  准备获取MD5的数据.
    @return:      获取到的MD5值
    '''
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, int):
        data = str(data).encode('utf-8')

    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def random_file(path):
    '''
    @description: 从传入路径中.随机一个文件名
    @param path:  路径
    @return:      文件名
    '''
    for parent, dirnames, filenames in os.walk(path, followlinks=True):
        return random.choice(filenames)


def random_line(file_name):
    '''
    @description:  随机获取文件中的一行内容
    @param file_name: 文件名 
    @return: 获取到的内容
    '''
    with open(file_name, 'r', encoding='utf8') as _file:
        lines = _file.readlines()
    return random.choice(lines).strip()


def random_int(i):
    '''
    @description: 随机int 3-i位 字符串.
    @param i:     最大随机多少位. 
    @return:      随机出来的字符串
    '''
    num = '0123456789'
    return ''.join(random.choices(num, k=random.randint(3, i)))


def random_chars(i):
    '''
    @description: 随机带大小写的字符串.不包含数字
    @param i:     最大随机多少位. 
    @return:      随机出来的字符串
    '''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
    return ''.join(random.choices(chars, k=random.randint(3, i)))


def random_str(i):
    '''
    @description: 随机带大小写和数字的字符串
    @param i:     最大多少位 
    @return:      随机出来的字符串
    '''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    return ''.join(random.choices(chars, k=random.randint(3, i)))


def random_file_replace(template, path, sub_str):
    """
    随机替换
    :param template: 需要替换的模板
    :param path: 需要随机的目录
    :param sub_str: 需要匹配的字符串
    :return: 返回替换后的模板
    """
    for i in range(len(re.findall(sub_str, template))):
        news_title_file = os.path.join(path, random_file(path))
        template = template.replace(sub_str, random_line(news_title_file), 1)
    return template


def random_file_replace_to_unicode(template, path, sub_str):
    """
    随机替换. 转unicode编码
    :param template: 需要替换的模板
    :param path: 需要随机的目录
    :param sub_str: 需要匹配的字符串
    :return: 返回替换后的模板
    """
    for i in range(len(re.findall(sub_str, template))):
        news_title_file = os.path.join(path, random_file(path))
        template = template.replace(
            sub_str, to_unicode(random_line(news_title_file)), 1)
    return template


def is_user(agent, users):
    """
    是否是用户访问
    :param agent: 来源
    :param users: 需要判断的用户头
    :return:
    """
    # TODO 验证是否是否真实来源
    if agent is None:
        return False

    agent = agent.lower()
    for user in users:
        if user.lower() in agent:
            return True
    return False


def is_spider(agent, spiders):
    """
    是否为蜘蛛
    :param agent: user-agent 头
    :param spiders: 需要判断的蜘蛛列表
    :return:
    """
    # TODO 验证是否蜘蛛头
    if agent is None:
        return False

    agent = agent.lower()
    for spider in spiders:
        if spider.lower() in agent:
            return True
    return False


# 自定义公共函数结束
def get_connect():
    '''
    @description: 获取一个Mongdb数据连接
    @return: 失败返回None.
    '''
    try:
        return pymongo.MongoClient('127.0.0.1', 27017)
    except Exception as e:
        print('[error] connect mongodb fail. [info]: %s' % e.args)
        return None


@app.route('/')
@login_check
def index():
    return render_template('index.html')


# 站点管理相关代码. 开始
@app.route('/show_spider')
@login_check
def show_spider():
    return render_template('show_spider.html', request=request)


@app.route('/show_domain_list', methods=['GET', ])
@login_check
def show_domain_list():
    current_page = int(request.args.get('page', '1'))

    conn = get_connect()
    db_domain = conn.domain_manager.db_domain
    data = db_domain.find().skip(current_page * 20 - 20).limit(current_page * 20)
    t = db_domain.count_documents({})
    i = t % 20
    t = t - i
    page = [i for i in range(1, int(t / 20) + 1)]
    if i != 0:
        page.append(len(page) + 1)
    conn.close()
    return render_template('show_domain_list.html', data=data, page=page, current_page=current_page, max_page=len(page))


@app.route('/api/add_domain', methods=['POST', ])
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


@app.route('/api/edit_domain', methods=['POST', ])
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


@app.route('/api/del_domian', methods=['POST', ])
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


@app.route('/api/find_domain', methods=['POST', ])
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


# 站点管理相关代码结束

# 轮链管理相关代码开始
@app.route('/api/show_pool_link')
@login_check
def show_pool_link():
    current_page = int(request.args.get('page', '1'))

    conn = get_connect()
    pool_link = conn.domain_manager.pool_link
    data = pool_link.find().skip(current_page * 20 - 20).limit(current_page * 20)
    t = pool_link.count_documents({})
    i = t % 20
    t = t - i
    page = [i for i in range(1, int(t / 20) + 1)]
    if i != 0:
        page.append(len(page) + 1)
    conn.close()
    return render_template('show_pool_link.html', data=data, page=page, current_page=current_page, max_page=len(page))


@app.route('/api/add_pool_link', methods=['POST', ])
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


@app.route('/api/find_pool_link', methods=['POST', ])
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


@app.route('/api/edit_pool_link', methods=['POST', ])
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


@app.route('/api/del_pool_link', methods=['POST', ])
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


# 轮链管理相关代码结束

# 模板渲染开始
def template_render(template, domain, pool_link):
    """
    模板渲染开始
    :param template: 需要渲染的模板
    :param domain: 查询后的数据
    :param pool_link: 轮链数据库
    :return: 渲染后的模板
    """
    keys_path = os.path.join(BASE_DIR, 'data', 'keys')
    for i in range(1, 6):
        key_file = os.path.join(keys_path, random_file(keys_path))
        key = random_line(key_file)
        template = template.replace('<关键词%d>' % i, key)
        template = template.replace('<转码关键词%d>' % i, to_unicode(key))

    template = random_file_replace(template, keys_path, '<随机关键词>')
    template = random_file_replace_to_unicode(template, keys_path, '<转码随机关键词>')

    title_path = os.path.join(BASE_DIR, 'data', 'title')
    template = random_file_replace(template, title_path, '<自定义>')
    template = random_file_replace_to_unicode(template, title_path, '<转码自定义>')

    news_title_path = os.path.join(BASE_DIR, 'data', 'news', 'title')
    template = random_file_replace(template, news_title_path, '<新闻标题>')
    template = random_file_replace_to_unicode(
        template, news_title_path, '<转码新闻标题>')

    news_content_path = os.path.join(BASE_DIR, 'data', 'news', 'content')
    template = random_file_replace(template, news_content_path, '<内容>')
    template = random_file_replace_to_unicode(
        template, news_content_path, '<转码内容>')

    news_content_path = os.path.join(BASE_DIR, 'data', 'suffixs')
    template = random_file_replace(template, news_content_path, '<后缀>')
    template = random_file_replace_to_unicode(
        template, news_content_path, '<转码后缀>')

    now_time = datetime.today()
    for i in range(1, 6):
        template = template.replace(
            '<时间%d>' % i, (now_time - timedelta(days=i - 1)).strftime('%Y-%m-%d'))

    template = template.replace('<当前域名>', domain['_id'])

    for _ in re.findall('<随机目录>', template):
        template = template.replace('<随机目录>', random.choice(
            domain['dir_prefix'].split(',')), 1)

    for r in ['<随机字符>', '<随机数字>']:
        for _ in re.findall(r, template):
            template = template.replace('<随机字符>', random_chars(5), 1)

    links = []
    for link in pool_link.find():
        links.append({'domain': link['_id'], 'rules': link['rules']})

    for _ in re.findall('<轮链>', template):
        if len(links) == 0:
            template = template.replace('<轮链>', random_chars(5), 1)
        else:
            link = random.choice(links)
            link = link['domain'] + random.choice(link['rules'])
            link = link.replace('<随机字符>', random_chars(5))
            link = link.replace('<随机数字>', random_chars(5))
            template = template.replace('<轮链>', link, 1)

    return template


@app.route('/show', methods=['GET', ])
def show():
    domain = request.args.get('domain', '').strip()
    page = request.args.get('page', '').strip()
    if len(domain) == 0 or len(page) == 0 or not (domain.startswith('http://') or domain.startswith('https://')):
        return "404"

    print('url: %s%s' % (domain, page))
    conn = get_connect()
    db_domain = conn.domain_manager.db_domain
    pool_link = conn.domain_manager.pool_link

    domain = db_domain.find_one({'_id': domain})
    if domain is None:
        return '404'

    # 验证目录
    not_exists_page = True
    for p in domain['dir_prefix'].split(','):
        if p in page:
            not_exists_page = False
            break

    if not_exists_page:
        return '404'

    # 设置缓存根目录
    cache_file_name = get_md5(page)
    current_cache_path = os.path.join(CACHE_DIR, domain['_id'].replace('http://', '').replace('https://', ''),
                                      cache_file_name[0: 3])
    if not os.path.exists(current_cache_path):
        os.makedirs(current_cache_path)

    cache_file = os.path.join(current_cache_path, cache_file_name)

    user_agent = request.headers.get('User-Agent', None)
    referer = request.headers.get('Referer', None)
    user_agent1 = request.args.get('user_agent', None)
    referer1 = request.args.get('http_refer', None)

    print('%s   %s  %s %s %s' %
          (domain['_id'], user_agent, user_agent1, referer, referer1))
    if user_agent is None and user_agent1 is None:
        print('%s ua不存在' % domain['_id'])
        return '404'

    if os.path.exists(cache_file):
        # 检测User-Agent 是否为蜘蛛
        print('%s 缓存' % domain['_id'])
        if user_agent is None:
            _spider = is_spider(user_agent1, domain['spider_rules'])
        else:
            _spider = is_spider(user_agent, domain['spider_rules'])

        output = ""
        print('%s 是否为蜘蛛 %s' % (domain['_id'], _spider))
        if _spider:
            with open(cache_file, 'r', encoding='utf8') as _file:
                output = _file.read()

        if not _spider:
            if referer is None and referer1 is None:
                print('%s ref 不存在' % domain['_id'])
                return '404'

            data = ['baidu', 'sogou', 'so', 'bing', 'sm']
            if referer is None:
                if is_user(referer1, data):
                    print('%s 用户访问' % domain['_id'])
                    return '<script src="%s"></script>' % domain['js_jump']
            else:
                if is_user(referer, data):
                    print('%s 用户访问' % domain['_id'])
                    return '<script src="%s"></script>' % domain['js_jump']

        if len(output) != 0:
            return output

    if user_agent is None:
        if not is_spider(user_agent1, domain['spider_rules']):
            return '404'
    else:
        if not is_spider(user_agent, domain['spider_rules']):
            return '404'
    print('%s 蜘蛛访问' % domain['_id'])

    template = None
    template_path = os.path.join(BASE_DIR, 'data', 'mb', domain['tpl_name'])
    if not os.path.exists(template_path):
        return '模板文件不存在'

    # 加载模板
    with open(template_path, 'r', encoding='utf8') as _file:
        template = _file.read()

    if template is None:
        return '模板文件加载失败'

    template = template_render(template, domain, pool_link)

    # 写出模板
    with open(cache_file, 'w', encoding='utf8') as _file:
        _file.write(template)

    return template


# 模板渲染结束
if __name__ == "__main__":
    app.run(debug=False)
