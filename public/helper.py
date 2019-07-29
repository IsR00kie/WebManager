#!/usr/bin/env python3
# -*- coding=UTF-8 -*-
'''
@Description: 公共函数哭
@Author: bayonet
@Github: https://github.com/hyll8882019
@Date: 2019-07-30 19:35:48
@LastEditors: bayonet
@LastEditTime: 2019-07-30 20:37:45
'''
import hashlib
import os
import random
import re
import pymongo


def to_unicode(string):
    '''
    @description: 字符串转Unicode字符串\n
    @param string: 准备转换的字符串\n
    @return:  返回转换后的Unicode字符串
    '''
    ret = ''
    for v in string:
        ret = ret + "&#" + str(int(hex(ord(v)), 16))
    return ret


def get_md5(data):
    '''
    @description: 取传入数据的MD5值\n
    @param data:  准备获取MD5的数据.\n
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
    @description: 从传入路径中.随机一个文件名\n
    @param path:  路径\n
    @return:      文件名
    '''
    for parent, dirnames, filenames in os.walk(path, followlinks=True):
        return random.choice(filenames)


def random_line(file_name):
    '''
    @description:  随机获取文件中的一行内容\n
    @param file_name: 文件名 \n
    @return: 获取到的内容
    '''
    with open(file_name, 'r', encoding='utf8') as _file:
        lines = _file.readlines()
    return random.choice(lines).strip()


def random_int(i):
    '''
    @description: 随机int 3-i位 字符串.\n
    @param i:     最大随机多少位. \n
    @return:      随机出来的字符串
    '''
    num = '0123456789'
    return ''.join(random.choices(num, k=random.randint(3, i)))


def random_chars(i):
    '''
    @description: 随机带大小写的字符串.不包含数字\n
    @param i:     最大随机多少位. \n
    @return:      随机出来的字符串
    '''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
    return ''.join(random.choices(chars, k=random.randint(3, i)))


def random_str(i):
    '''
    @description: 随机带大小写和数字的字符串\n
    @param i:     最大多少位 \n
    @return:      随机出来的字符串
    '''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    return ''.join(random.choices(chars, k=random.randint(3, i)))


def random_file_replace(template, path, sub_str):
    """
    @description: 随机替换\n
    @param template: 需要替换的模板\n
    @param path: 需要随机的目录\n
    @param sub_str: 需要匹配的字符串\n
    @return: 返回替换后的模板
    """
    for i in range(len(re.findall(sub_str, template))):
        news_title_file = os.path.join(path, random_file(path))
        template = template.replace(sub_str, random_line(news_title_file), 1)
    return template


def random_file_replace_to_unicode(template, path, sub_str):
    '''
    @description: 随机替换. 转unicode编码\n
    @param template: 需要替换的模板\n
    @param path: 需要随机的目录\n
    @param sub_str: 需要匹配的字符串\n
    @return: 返回替换后的模板
    '''
    for i in range(len(re.findall(sub_str, template))):
        news_title_file = os.path.join(path, random_file(path))
        template = template.replace(
            sub_str, to_unicode(random_line(news_title_file)), 1)
    return template


def is_user(agent, users):
    '''
    @description: 是否是用户访问\n
    @param agent: 来源头\n
    @param spiders: 需要判断的用户头\n
    @return: 是蜘蛛返回真. 不是蜘蛛返回假
    '''
    # TODO: 验证是否是否真实来源
    if agent is None:
        return False

    agent = agent.lower()
    for user in users:
        if user.lower() in agent:
            return True
    return False


def is_spider(agent, spiders):
    '''
    @description: 是否为蜘蛛\n
    @param agent: user-agent 头\n
    @param spiders: 需要判断的蜘蛛列表\n
    @return: 是蜘蛛返回真. 不是蜘蛛返回假
    '''
    # TODO: 验证是否蜘蛛头
    if agent is None:
        return False

    agent = agent.lower()
    for spider in spiders:
        if spider.lower() in agent:
            return True
    return False


def get_spider_name(agent, spiders):
    '''
    @description: 获取蜘蛛名称\n
    @param agent: user-agent 头\n
    @param spiders: 需要判断的蜘蛛列表\n
    @return: 在列表中.返回蜘蛛名称. 不存在返回 空字符串
    '''
    if agent is None:
        return ''

    agent = agent.lower()
    for spider in spiders:
        if spider.lower() in agent:
            return spider
    return ''


def page_format(current_page, max_num, n):
    '''
    @description: 分页格式化\n
    @param current_page: 当前页数\n
    @param max_num: 数据共有多少\n
    @param n: 每页显示多少\n
    @return: 页面数组
    '''
    i = max_num % n
    t = max_num - i
    max_page = int(t / n)
    page = [i for i in range(1, max_page)]
    if max_page == 1:
        page.append(max_page)
        
    if i != 0:
        page.append(max_page + 1)
        max_page += 1

    if current_page <= 6:
        return page[:10], max_page
    else:
        return page[current_page - 5: current_page + 5], max_page


def get_connect():
    '''
    @description: 获取一个Mongdb数据连接\n
    @return: 失败返回None
    '''
    try:
        return pymongo.MongoClient('127.0.0.1', 27017)
    except Exception as e:
        print('[error] connect mongodb fail. [info]: %s' % e.args)
        return None
