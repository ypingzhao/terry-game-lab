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

def fetch_rss(source):
    """从RSS源抓取新闻"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; TerryGameLab/1.0)'
        }
        response = requests.get(source['url'], headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析XML
        root = ET.fromstring(response.content)
        channel = root.find('channel')
        items = channel.findall('item') if channel else []
        
        news_list = []
        for item in items[:MAX_ITEMS_PER_SOURCE]:
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            description = item.find('description').text if item.find('description') is not None else ''
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            
            # 解析时间
            try:
                if pubDate:
                    # 解析RSS时间格式
                    dt = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %Z')
                    timestamp = int(dt.timestamp() * 1000)
                else:
                    timestamp = int(time.time() * 1000)
            except Exception:
                timestamp = int(time.time() * 1000)
            
            # 处理分类 - 支持多个标签
            categories = source.get('categories', [])
            if not categories and 'category' in source:
                categories = [source['category']]
            
            # 清理描述
            if description:
                # 去掉HTML标签，截断
                import re
                description = re.sub(r'<[^>]*>', '', description)
                description = description[:200] + '...' if len(description) > 200 else description
            
            news_list.append({
                'title': title.strip() if title else '',
                'link': link.strip() if link else '',
                'summary': description.strip() if description else '',
                'time': timestamp,
                'source': source['name'],
                'categories': categories,
                'sourceColor': source.get('color', 'rgba(0, 255, 255, 0.3)')
            })
            
        print(f"✅ {source['name']}: 获取到 {len(news_list)} 条新闻")
        return news_list
        
    except Exception as e:
        print(f"❌ {source['name']}: 获取失败 - {str(e)}")
        return []

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
    for source in sources:
        news = fetch_rss(source)
        all_new_news.extend(news)
        time.sleep(1)  # 礼貌延迟
    
    print("-" * 40)
    print(f"📥 总共抓取到 {len(all_new_news)} 条新闻")
    
    # 合并
    merged = merge_news(existing_news, all_new_news)
    print(f"🔗 合并后共 {len(merged)} 条新闻（去重+过滤过期）")
    
    # 保存
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    print(f"💾 已保存到 {CACHE_FILE}")
    print("\n下一步: git add cached-news.json && git commit && git push")
    print("推送后网站就会显示更新后的新闻了")

if __name__ == '__main__':
    main()
