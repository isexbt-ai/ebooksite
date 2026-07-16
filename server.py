#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
图书管理系统 - 服务启动入口
"""

import os
import sys
import logging
import tornado.ioloop
import tornado.web
import tornado.httpserver

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from webserver.settings import CONF
from webserver.handlers import routes


def make_app():
    """创建 Tornado 应用"""
    settings = {
        'cookie_secret': CONF['cookie_secret'],
        'login_url': '/login',
        'debug': CONF.get('debug', False),
        'static_path': os.path.join(BASE_DIR, 'app', '.output', 'public'),
        'template_path': os.path.join(BASE_DIR, 'webserver', 'templates'),
    }

    return tornado.web.Application(routes, **settings)


def main():
    """主函数"""
    app = make_app()

    port = CONF.get('port', 8080)
    server = tornado.httpserver.HTTPServer(app)
    server.bind(port)
    server.start(1)

    logger.info(f'服务已启动，监听端口: {port}')
    logger.info(f'访问地址: http://127.0.0.1:{port}')

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logger.info('服务正在关闭...')
        tornado.ioloop.IOLoop.current().stop()


if __name__ == '__main__':
    main()
