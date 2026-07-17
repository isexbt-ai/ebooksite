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


class IndexHandler(tornado.web.RequestHandler):
    """首页 Handler - 返回静态 index.html"""

    def get(self):
        """返回首页"""
        index_path = os.path.join(BASE_DIR, 'app', '.output', 'public', 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'rb') as f:
                self.set_header('Content-Type', 'text/html; charset=utf-8')
                self.write(f.read())
        else:
            self.set_status(404)
            self.write("index.html not found. Please build the frontend first.")


class StaticFileHandler(tornado.web.StaticFileHandler):
    """静态文件 Handler"""
    pass


def make_app():
    """创建 Tornado 应用"""
    settings = {
        'cookie_secret': CONF['cookie_secret'],
        'login_url': '/login',
        'debug': CONF.get('debug', False),
        'xsrf_cookies': False,  # 禁用 CSRF，因为使用 API token 认证
    }

    # 静态文件目录
    static_path = os.path.join(BASE_DIR, 'app', '.output', 'public')

    # 路由列表
    app_routes = routes.copy()

    # 添加 API 路由
    # routes 已经包含 /api/* 路由

    # 添加静态文件路由（如果目录存在）
    if os.path.exists(static_path):
        # _nuxt 静态资源服务
        app_routes.insert(0, (
            r"/_nuxt/(.*)",
            tornado.web.StaticFileHandler,
            {"path": os.path.join(static_path, '_nuxt')}
        ))

        # 根路径返回 index.html
        app_routes.insert(0, (r"/", IndexHandler))

        # 其他前端路由也返回 index.html（SPA 模式）
        app_routes.append((r"/.*", IndexHandler))
    else:
        logger.warning(f"静态文件目录不存在: {static_path}")
        logger.warning("请运行: cd app && npm install && npm run build")

    return tornado.web.Application(app_routes, **settings)


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
