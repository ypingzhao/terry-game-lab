#!/usr/bin/env python3
"""
新闻抓取脚本
运行方式: python fetch-news.py
功能: 从配置的RSS源抓取新闻，合并到cached-news.json，自动去重保留最近90天
"""

import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import os

# 配置
NEWS_SOURCES_FILE = 'news-sources.json'
CACHE_FILE = 'cached-news.json'
MAX_ITEMS_PER_SOURCE = 10  # 每个源最多抓取多少条
MAX_TOTAL_ITEMS = 200      # 总缓存最多保留多少条
DAYS_TO_KEEP = 90          # 保留多少天内的新闻

def load_sources():
    """加载新闻源配置"""
    with open(NEWS_SOURCES_FILE, 'r', encoding='utf-8') as f:
        sources = json.load(f)
    return [s for s in sources if s.get('enabled', True)]

def fetch_rss(source, max_retries=3):
    """从RSS源抓取新闻，带重试机制"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; TerryGameLab/1.0; +https://github.com/ypingzhao/terry-game-lab)'
    }
    
    for retry in range(max_retries):
        try:
            response = requests.get(source['url'], headers=headers, timeout=15)
            response.raise_for_status()
            
            # 检测是否是HTML错误页而不是RSS
            content = response.content
            if len(content) < 100 or b'<html' in content.lower() and b'<rss' not in content.lower():
                raise ValueError("返回不是RSS XML格式，可能被拦截")
            
            # 解析XML
            # 处理可能的命名空间
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            root = ET.fromstring(content, parser=parser)
            
            # 支持不同的RSS格式（rss / rdf:RDF）
            channel = root.find('channel')
            if channel is not None:
                items = channel.findall('item')
            else:
                # 支持RDF格式
                items = root.findall('.//item')
            
            if not items:
                print(f"⚠️  {source['name']}: RSS返回为空 (尝试 {retry+1}/{max_retries})")
                time.sleep(2)
                continue
            
            news_list = []
            for item in items[:MAX_ITEMS_PER_SOURCE]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else None
                
                # 如果没有pubDate，尝试dc:date
                if pubDate is None:
                    for ns in ['dc:date', 'dc:pubDate', '{http://purl.org/dc/elements/1.1/}date']:
                        date_elem = item.find(ns)
                        if date_elem is not None and date_elem.text:
                            pubDate = date_elem.text
                            break
                
                # 解析时间，支持多种格式
                timestamp = int(time.time() * 1000)
                if pubDate:
                    timestamp = parse_date(pubDate) or timestamp
                
                # 处理分类 - 支持多个标签
                categories = source.get('categories', [])
                if not categories and 'category' in source:
                    categories = [source['category']]
                
                # 清理描述
                if description:
                    # 去掉HTML标签，截断
                    import re
                    description = re.sub(r'<[^>]*>', '', description)
                    description = description.strip()
                    description = description[:200] + '...' if len(description) > 200 else description
                
                if title and link:  # 只保存有标题和链接的新闻
                    news_list.append({
                        'title': title.strip(),
                        'link': link.strip(),
                        'summary': description.strip() if description else '',
                        'time': timestamp,
                        'source': source['name'],
                        'categories': categories,
                        'sourceColor': source.get('color', 'rgba(0, 255, 255, 0.3)')
                    })
            
            if len(news_list) > 0:
                print(f"✅ {source['name']}: 获取到 {len(news_list)} 条新闻 (尝试 {retry+1}/{max_retries})")
                return news_list
            else:
                print(f"⚠️  {source['name']}: 没有获取到有效新闻 (尝试 {retry+1}/{max_retries})")
                
        except Exception as e:
            print(f"❌ {source['name']}: 获取失败 (尝试 {retry+1}/{max_retries}) - {str(e)}")
        
        # 重试前等待
        if retry < max_retries - 1:
            time.sleep(2 ** (retry + 1))  # 指数退避
    
    print(f"💀 {source['name']}: 多次尝试后仍然失败，跳过")
    return []


def parse_date(date_str):
    """尝试多种格式解析日期，返回毫秒时间戳"""
    formats = [
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S %z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return int(dt.timestamp() * 1000)
        except:
            continue
    
    # 尝试解析为ISO格式
    try:
        from dateutil.parser import parse as parse_iso
        dt = parse_iso(date_str)
        return int(dt.timestamp() * 1000)
    except:
        pass
    
    return None

def merge_news(existing_news, new_news):
    """合并新闻，按URL去重，保留最新"""
    url_map = {}
    
    # 添加已有新闻
    for news in existing_news:
        if 'link' in news and news['link']:
            url_map[news['link']] = news
    
    # 添加新新闻（会覆盖相同URL，保证最新）
    for news in new_news:
        if 'link' in news and news['link']:
            url_map[news['link']] = news
    
    # 转回数组
    merged = list(url_map.values())
    
    # 按时间倒序
    merged.sort(key=lambda x: x['time'], reverse=True)
    
    # 过滤掉过期新闻
    cutoff_time = int((datetime.now() - timedelta(days=DAYS_TO_KEEP)).timestamp() * 1000)
    merged = [n for n in merged if n['time'] > cutoff_time]
    
    # 限制总数
    if len(merged) > MAX_TOTAL_ITEMS:
        merged = merged[:MAX_TOTAL_ITEMS]
    
    return merged

def main():
    print("🚀 Terry Game Lab 新闻抓取工具")
    print("-" * 40)
    
    # 加载新闻源
    sources = load_sources()
    print(f"📋 加载了 {len(sources)} 个启用的新闻源")
    
    # 加载已有缓存
    existing_news = []
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                existing_news = json.load(f)
                print(f"📂 已有缓存 {len(existing_news)} 条新闻")
            except:
                print("⚠️ 缓存文件损坏，将创建新缓存")
                existing_news = []
    
    # 抓取所有新闻源
    all_new_news = []
    success_count = 0
    fail_count = 0
    
    for i, source in enumerate(sources):
        news = fetch_rss(source)
        if len(news) > 0:
            all_new_news.extend(news)
            success_count += 1
        else:
            fail_count += 1
        # 礼貌延迟，避免被封
        if i < len(sources) - 1:
            time.sleep(2)
    
    print("-" * 40)
    print(f"📥 总共抓取到 {len(all_new_news)} 条新闻 (成功: {success_count} 源, 失败: {fail_count} 源)")
    
    # 如果完全失败，保持原有缓存不覆盖
    if len(all_new_news) == 0 and len(existing_news) > 0:
        print("⚠️  所有源都抓取失败，保持原有缓存不变")
        exit(0)
    
    # 合并
    merged = merge_news(existing_news, all_new_news)
    print(f"🔗 合并后共 {len(merged)} 条新闻（去重+过滤过期）")
    
    # 保存
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    print(f"💾 已保存到 {CACHE_FILE}")
    
    # 如果没有任何新闻，退出码非0让GitHub Action知道失败了
    if len(merged) == 0:
        print("❌ 最终没有任何新闻，保存了空文件")
        exit(1)
    else:
        print("✅ 完成!")
        exit(0)

if __name__ == '__main__':
    main()
