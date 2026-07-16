#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
下载管理 Handler
"""

import logging
import aiohttp
import os
from datetime import datetime

from webserver.handlers.base import BaseHandler, auth_required
from webserver.models import DownloadLog, BookSource
from webserver.settings import CONF

logger = logging.getLogger(__name__)


class DownloadHandler(BaseHandler):
    """下载 Handler"""

    def _get_post_data(self):
        """获取 POST 请求数据，支持 form-data 和 JSON"""
        content_type = self.request.headers.get('Content-Type', '')
        if content_type.startswith('application/json'):
            try:
                body = self.request.body
                if body:
                    return json.loads(body.decode('utf-8'))
                return {}
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {}
        else:
            # form-data 格式
            result = {}
            for key, values in self.request.body_arguments.items():
                if values:
                    result[key] = values[0].decode('utf-8')
            return result

    @auth_required
    async def post(self):
        """开始下载"""
        try:
            data = self._get_post_data()
            title = data.get('title', '')
            author = data.get('author', '')
            download_url = data.get('download_url', '')
            source_id = data.get('source_id', '')

            if not download_url:
                return self.write_error("invalid_params", "下载链接不能为空")

            # 获取当前用户
            user = self.get_current_user()

            # 创建下载记录
            log = DownloadLog.create(
                user_id=user.id,
                book_title=title,
                book_author=author,
                source_id=int(source_id) if source_id else None,
                source_url=download_url,
            )

            # 异步下载
            self.download_file(log.id, download_url)

            return self.write_success({
                "download_id": log.id,
                "status": "downloading",
            })

        except Exception as e:
            logger.error(f"开始下载失败: {e}")
            return self.write_error("download_failed", "开始下载失败")

    async def download_file(self, log_id: int, url: str):
        """异步下载文件"""
        try:
            log = DownloadLog.get_by_id(log_id)
            if not log:
                return

            # 更新状态为下载中
            log.update_status('downloading')

            # 下载文件
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    if response.status != 200:
                        log.update_status('failed')
                        return

                    # 获取文件名
                    content_disposition = response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=')[1].strip('"\'')
                    else:
                        filename = os.path.basename(url.split('?')[0]) or 'download'

                    # 保存文件
                    file_path = os.path.join(CONF['uploads_dir'], f"{log_id}_{filename}")
                    total_size = 0

                    with open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            total_size += len(chunk)

                    # 更新状态为完成
                    log.update_status('completed', file_path, total_size)

        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            try:
                log = DownloadLog.get_by_id(log_id)
                if log:
                    log.update_status('failed')
            except:
                pass


class DownloadStatusHandler(BaseHandler):
    """下载状态 Handler"""

    @auth_required
    def get(self, download_id):
        """获取下载状态"""
        try:
            log = DownloadLog.get_by_id(int(download_id))
            if not log:
                return self.write_error("not_found", "下载记录不存在")

            return self.write_success(log.to_dict())

        except Exception as e:
            logger.error(f"获取下载状态失败: {e}")
            return self.write_error("status_failed", "获取下载状态失败")


class DownloadHistoryHandler(BaseHandler):
    """下载历史 Handler"""

    @auth_required
    def get(self):
        """获取下载历史"""
        try:
            page = int(self.get_argument('page', '1'))
            size = int(self.get_argument('size', '20'))

            user = self.get_current_user()
            logs = DownloadLog.get_by_user(user.id, page, size)

            return self.write_success({
                "total": len(logs),
                "items": [log.to_dict() for log in logs],
                "page": page,
            })

        except Exception as e:
            logger.error(f"获取下载历史失败: {e}")
            return self.write_error("history_failed", "获取下载历史失败")
