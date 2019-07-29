#!/usr/bin/env python3
# -*- coding=UTF-8 -*-
'''
@Description: 项目初始化
@Author: bayonet
@Github: https://github.com/hyll8882019
@Date: 2019-07-28 21:24:41
@LastEditors: bayonet
@LastEditTime: 2019-07-30 00:29:09
'''
from main import get_connect
import os

ROOT_BASE = os.path.dirname(os.path.abspath(__file__))


def create_dir(path):
    data = os.path.join(ROOT_BASE, 'data')
    if not os.path.exists(data):
        print('[+] 正在创建 %s 目录' % path)
        os.mkdir(data)
    else:
        print('[+] 存在这个 %s 目录, 不进行创建' % path)


def create_mongodb_index():
    ''' @description: 创建mongodb索引 '''
    print('[+] 正在创建mongodb缓存索引')
    conn = get_connect()
    spider_log = conn.domain_manager.spider_log
    spider_log.create_index('create_time', expireAfterSeconds=60 * 60 * 24 * 3)  # 蜘蛛数据3天后自动删除
    conn.close()


def init():
    create_mongodb_index()
    for p in ['data', 'data/cache', 'data/keys', 'data/mb',
              'data/news', 'data/suffixs', 'data/title',
              'data/news/title', 'data/news/content']:
        create_dir(p)


if __name__ == "__main__":
    init()
