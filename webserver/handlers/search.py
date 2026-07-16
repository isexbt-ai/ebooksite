#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
网络书库搜索 Handler
支持 OPDS、API 书源
"""

import logging
import aiohttp
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

from tornado.web import RequestHandler
from webserver.handlers.base import BaseHandler, auth_required
from webserver.models import BookSource

logger = logging.getLogger(__name__)


class SearchHandler(BaseHandler):
    """搜索 Handler"""

    async def get(self):
        """搜索书籍"""
        query = self.get_argument('query', '')
        source_id = self.get_argument('source', '')
        page = int(self.get_argument('page', '1'))

        if not query:
            return self.write_error("invalid_params", "请输入搜索关键词")

        try:
            # 获取书源
            if source_id:
                sources = [BookSource.get_by_id(int(source_id))]
            else:
                sources = BookSource.get_all(enabled_only=True)

            # 并行搜索
            results = []
            for source in sources:
                if not source:
                    continue
                try:
                    if source.type == 'opds':
                        items = await self.search_opds(source, query, page)
                    elif source.type == 'api':
                        items = await self.search_api(source, query, page)
                    else:
                        continue

                    results.extend(items)
                except Exception as e:
                    logger.error(f"搜索书源 {source.name} 失败: {e}")

            return self.write_success({
                "total": len(results),
                "items": results,
                "page": page,
            })

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return self.write_error("search_failed", "搜索失败，请稍后重试")

    async def search_opds(self, source: BookSource, query: str, page: int) -> list:
        """搜索 OPDS 书源"""
        url = urljoin(source.url, f"search/{query}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return []

                xml_data = await response.text()
                return self.parse_opds(xml_data, source)

    async def search_api(self, source: BookSource, query: str, page: int) -> list:
        """搜索 API 书源"""
        url = urljoin(source.url, "search")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params={'q': query, 'page': page},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                return data.get('items', [])

    def parse_opds(self, xml_data: str, source: BookSource) -> list:
        """解析 OPDS XML"""
        try:
            root = ET.fromstring(xml_data)
            items = []

            # 解析 entry 元素
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                item = {
                    'id': entry.findtext('{http://www.w3.org/2005/Atom}id', ''),
                    'title': entry.findtext('{http://www.w3.org/2005/Atom}title', ''),
                    'author': entry.findtext('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name', ''),
                    'summary': entry.findtext('{http://www.w3.org/2005/Atom}summary', ''),
                    'source': source.name,
                    'source_id': source.id,
                }

                # 获取封面链接
                for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                    rel = link.get('rel', '')
                    href = link.get('href', '')
                    if 'image' in rel or 'cover' in rel:
                        item['cover_url'] = href
                    elif 'acquisition' in rel:
                        item['download_url'] = href

                items.append(item)

            return items
        except ET.ParseError as e:
            logger.error(f"解析 OPDS XML 失败: {e}")
            return []
