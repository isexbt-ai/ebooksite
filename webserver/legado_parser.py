#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Legado 书源解析器
支持解析 Legado 格式的书源 JSON，提取搜索规则、书籍信息规则、章节规则等
"""

import json
import re
import logging
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class LegadoSource:
    """Legado 书源模型"""

    def __init__(self, data: dict):
        self.raw = data
        self.book_source_url = data.get('bookSourceUrl', '')
        self.book_source_name = data.get('bookSourceName', '')
        self.book_source_group = data.get('bookSourceGroup', '')
        self.book_source_type = data.get('bookSourceType', 0)  # 0:text, 1:audio
        self.login_url = data.get('loginUrl', '')
        self.header = data.get('header', '')
        self.enabled = data.get('enabled', True)
        self.enabled_explore = data.get('enabledExplore', True)
        self.explore_url = data.get('exploreUrl', '')
        self.weight = data.get('weight', 0)
        self.custom_order = data.get('customOrder', 0)
        self.last_update_time = data.get('lastUpdateTime', 0)
        self.rule_search = data.get('ruleSearch', {})
        self.rule_book_info = data.get('ruleBookInfo', {})
        self.rule_toc = data.get('ruleToc', {})
        self.rule_content = data.get('ruleContent', {})
        self.rule_explore = data.get('ruleExplore', {})
        self.search_url = data.get('searchUrl', '')
        self.book_url_pattern = data.get('bookUrlPattern', '')

    @property
    def is_text(self) -> bool:
        """是否为文本书源"""
        return self.book_source_type == 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'bookSourceUrl': self.book_source_url,
            'bookSourceName': self.book_source_name,
            'bookSourceGroup': self.book_source_group,
            'bookSourceType': self.book_source_type,
            'enabled': self.enabled,
            'searchUrl': self.search_url,
            'ruleSearch': self.rule_search,
            'ruleBookInfo': self.rule_book_info,
            'ruleToc': self.rule_toc,
            'ruleContent': self.rule_content,
        }


class LegadoParser:
    """Legado 书源解析器"""

    @staticmethod
    def parse_json(json_data: str) -> Optional[LegadoSource]:
        """解析单个 Legado 书源 JSON"""
        try:
            data = json.loads(json_data)
            return LegadoSource(data)
        except json.JSONDecodeError as e:
            logger.error(f"解析 Legado 书源 JSON 失败: {e}")
            return None

    @staticmethod
    def parse_json_array(json_data: str) -> List[LegadoSource]:
        """解析 Legado 书源 JSON 数组"""
        sources = []
        try:
            data = json.loads(json_data)
            if isinstance(data, list):
                for item in data:
                    try:
                        sources.append(LegadoSource(item))
                    except Exception as e:
                        logger.warning(f"解析单个书源失败: {e}")
            elif isinstance(data, dict):
                sources.append(LegadoSource(data))
        except json.JSONDecodeError as e:
            logger.error(f"解析 Legado 书源 JSON 数组失败: {e}")
        return sources

    @staticmethod
    def build_search_url(source: LegadoSource, keyword: str, page: int = 1) -> str:
        """
        构建搜索 URL
        支持 {{key}}, {{page}} 等模板变量替换
        """
        search_url = source.search_url
        if not search_url:
            return ''

        # 处理 URL 选项参数（JSON 格式）
        url_part = search_url
        options = {}
        if search_url.startswith('{'):
            # 纯 JSON 格式，直接返回
            return search_url

        # 分离 URL 和选项
        if ',{' in search_url:
            parts = search_url.split(',{', 1)
            url_part = parts[0]
            try:
                options = json.loads('{' + parts[1])
            except:
                pass

        # 替换模板变量
        # {{key}} -> 搜索关键词
        url_part = url_part.replace('{{key}}', keyword)

        # {{page}} -> 页码
        url_part = url_part.replace('{{page}}', str(page))

        # {{(page-1)*20}} 等计算表达式
        page_match = re.search(r'\{\{\s*\(?\s*page\s*[-+]\s*(\d+)\s*\)?\s*\*\s*(\d+)\s*\}\}', url_part)
        if page_match:
            offset = int(page_match.group(1))
            multiplier = int(page_match.group(2))
            value = (page - 1 - offset) * multiplier if page > 1 else 0
            url_part = url_part[:page_match.start()] + str(value) + url_part[page_match.end():]

        # 处理 page-1 == 0 ? "" : page 这种条件表达式
        # 简化为：第一页不加页码参数
        if '{{page - 1 == 0' in url_part or '{{page-1==0' in url_part:
            if page == 1:
                url_part = re.sub(r'\{\{page\s*[-+]\s*1\s*==\s*0\s*\?\s*"[^"]*"\s*:\s*[^}]*\}\}', '', url_part)
            else:
                url_part = re.sub(r'\{\{page\s*[-+]\s*1\s*==\s*0\s*\?\s*"[^"]*"\s*:\s*"?([^"}]*)"?\}\}', r'\1', url_part)

        # 确保 URL 是完整的
        if url_part.startswith('/'):
            parsed = urlparse(source.book_source_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            url_part = base + url_part
        elif not url_part.startswith('http'):
            url_part = urljoin(source.book_source_url, url_part)

        # 如果有选项，重新组合
        if options:
            return f"{url_part},{json.dumps(options, ensure_ascii=False)}"

        return url_part

    @staticmethod
    def extract_search_rules(source: LegadoSource) -> Dict[str, str]:
        """提取搜索规则"""
        rules = source.rule_search
        return {
            'book_list': rules.get('bookList', ''),
            'name': rules.get('name', ''),
            'author': rules.get('author', ''),
            'cover_url': rules.get('coverUrl', ''),
            'intro': rules.get('intro', ''),
            'book_url': rules.get('bookUrl', ''),
            'kind': rules.get('kind', ''),
            'last_chapter': rules.get('lastChapter', ''),
            'word_count': rules.get('wordCount', ''),
        }

    @staticmethod
    def extract_book_info_rules(source: LegadoSource) -> Dict[str, str]:
        """提取书籍信息规则"""
        rules = source.rule_book_info
        return {
            'name': rules.get('name', ''),
            'author': rules.get('author', ''),
            'cover_url': rules.get('coverUrl', ''),
            'intro': rules.get('intro', ''),
            'kind': rules.get('kind', ''),
            'last_chapter': rules.get('lastChapter', ''),
            'toc_url': rules.get('tocUrl', ''),
        }

    @staticmethod
    def extract_toc_rules(source: LegadoSource) -> Dict[str, str]:
        """提取章节列表规则"""
        rules = source.rule_toc
        return {
            'chapter_list': rules.get('chapterList', ''),
            'chapter_name': rules.get('chapterName', ''),
            'chapter_url': rules.get('chapterUrl', ''),
            'next_toc_url': rules.get('nextTocUrl', ''),
        }

    @staticmethod
    def extract_content_rules(source: LegadoSource) -> Dict[str, str]:
        """提取正文内容规则"""
        rules = source.rule_content
        return {
            'content': rules.get('content', ''),
            'next_content_url': rules.get('nextContentUrl', ''),
            'web_js': rules.get('webJs', ''),
        }

    @staticmethod
    def is_valid_source(data: dict) -> bool:
        """验证是否为有效的 Legado 书源"""
        required_fields = ['bookSourceUrl', 'bookSourceName']
        return all(field in data and data[field] for field in required_fields)

    @staticmethod
    def detect_rule_type(rule: str) -> str:
        """
        检测规则类型
        返回: css, xpath, jsonpath, regex, js
        """
        if not rule:
            return 'unknown'

        rule = rule.strip()

        if rule.startswith('@css:'):
            return 'css'
        elif rule.startswith('@XPath:') or rule.startswith('//'):
            return 'xpath'
        elif rule.startswith('@json:') or rule.startswith('$.') or rule.startswith('$..'):
            return 'jsonpath'
        elif rule.startswith('@js:'):
            return 'js'
        elif rule.startswith('<js>') or rule.startswith('@js:'):
            return 'js'
        elif rule.startswith(':'):
            return 'regex'
        elif '##' in rule:
            return 'regex'
        elif rule.startswith('@'):
            return 'css'  # 默认 JSOUP CSS
        else:
            return 'css'  # 默认 CSS


class RuleExecutor:
    """规则执行器 - 用于执行各种解析规则"""

    @staticmethod
    def execute_css(html: str, rule: str) -> List[str]:
        """执行 CSS 选择器规则"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # 解析规则，提取选择器和属性
            # 格式: selector@attr 或 selector@text
            if '@' in rule:
                parts = rule.rsplit('@', 1)
                selector = parts[0]
                attr = parts[1]
            else:
                selector = rule
                attr = 'text'

            elements = soup.select(selector)
            results = []

            for elem in elements:
                if attr == 'text':
                    results.append(elem.get_text(strip=True))
                elif attr == 'textNodes':
                    results.append(elem.get_text())
                elif attr == 'html':
                    results.append(str(elem))
                elif attr == 'all':
                    results.append(str(elem))
                else:
                    results.append(elem.get(attr, ''))

            return results
        except Exception as e:
            logger.error(f"CSS 规则执行失败: {e}")
            return []

    @staticmethod
    def execute_xpath(html: str, rule: str) -> List[str]:
        """执行 XPath 规则"""
        try:
            from lxml import etree
            tree = etree.HTML(html)
            results = tree.xpath(rule)
            return [str(r) for r in results]
        except Exception as e:
            logger.error(f"XPath 规则执行失败: {e}")
            return []

    @staticmethod
    def execute_jsonpath(data: Any, rule: str) -> List[Any]:
        """执行 JSONPath 规则"""
        try:
            import jsonpath_ng
            from jsonpath_ng import parse
            jsonpath_expr = parse(rule)
            results = [match.value for match in jsonpath_expr.find(data)]
            return results
        except ImportError:
            # 简单的 JSONPath 实现
            return RuleExecutor._simple_jsonpath(data, rule)
        except Exception as e:
            logger.error(f"JSONPath 规则执行失败: {e}")
            return []

    @staticmethod
    def _simple_jsonpath(data: Any, rule: str) -> List[Any]:
        """简单的 JSONPath 实现"""
        try:
            if rule.startswith('$.'):
                rule = rule[2:]
            elif rule.startswith('$..'):
                rule = rule[3:]

            parts = rule.split('.')
            current = data

            for part in parts:
                if part == '*':
                    if isinstance(current, list) and current:
                        return current
                    return []
                elif part.endswith('[*]'):
                    key = part[:-3]
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    if isinstance(current, list):
                        return current
                    return []
                else:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return []

            if isinstance(current, list):
                return current
            return [current]
        except Exception as e:
            logger.error(f"简单 JSONPath 执行失败: {e}")
            return []

    @staticmethod
    def execute_regex(text: str, pattern: str) -> List[str]:
        """执行正则规则"""
        try:
            matches = re.findall(pattern, text)
            return [str(m) for m in matches]
        except Exception as e:
            logger.error(f"正则规则执行失败: {e}")
            return []

    @staticmethod
    def apply_rule(html_or_data: Any, rule: str, rule_type: str = None) -> List[Any]:
        """应用规则获取结果"""
        if not rule:
            return []

        if not rule_type:
            rule_type = LegadoParser.detect_rule_type(rule)

        try:
            if rule_type == 'css':
                # 去除 @css: 前缀
                if rule.startswith('@css:'):
                    rule = rule[5:]
                elif rule.startswith('@'):
                    rule = rule[1:]
                return RuleExecutor.execute_css(html_or_data, rule)
            elif rule_type == 'xpath':
                if rule.startswith('@XPath:'):
                    rule = rule[7:]
                return RuleExecutor.execute_xpath(html_or_data, rule)
            elif rule_type == 'jsonpath':
                if rule.startswith('@json:'):
                    rule = rule[6:]
                if isinstance(html_or_data, str):
                    data = json.loads(html_or_data)
                else:
                    data = html_or_data
                return RuleExecutor.execute_jsonpath(data, rule)
            elif rule_type == 'regex':
                # 处理 ##正则##替换 格式
                if '##' in rule:
                    parts = rule.split('##')
                    if len(parts) >= 3:
                        pattern = parts[1]
                        return RuleExecutor.execute_regex(html_or_data, pattern)
                return []
            else:
                return []
        except Exception as e:
            logger.error(f"应用规则失败: {e}")
            return []


def parse_legado_sources(json_text: str) -> List[LegadoSource]:
    """
    解析 Legado 书源 JSON 文本
    支持单个书源或书源数组
    """
    parser = LegadoParser()
    json_text = json_text.strip()

    try:
        data = json.loads(json_text)
        if isinstance(data, list):
            sources = []
            for item in data:
                if LegadoParser.is_valid_source(item):
                    sources.append(LegadoSource(item))
            return sources
        elif isinstance(data, dict):
            if LegadoParser.is_valid_source(data):
                return [LegadoSource(data)]
    except json.JSONDecodeError:
        logger.error("无效的 JSON 格式")

    return []
