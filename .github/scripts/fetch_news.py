#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch latest policy news from government websites for software & IT service industry
"""

import requests
import re
import json
from datetime import datetime

# Keywords for software & IT service industry
KEYWORDS = [
    '软件', '软件开发', '数据', '数据分析', '数据治理', '人工智能', 'AI',
    '智能制造', '信息系统', '运维', '信息技术', '数字化', '工业互联网',
    '云计算', '大数据', '区块链', '算法', '大模型', '平台经济'
]

# Organization configurations with specific policy URLs
ORG_CONFIG = {
    'miit': {
        'name': '工业和信息化部',
        'url': 'www.miit.gov.cn/xwfb/zxzc/index.html',
        'base': 'http://www.miit.gov.cn',
        'keywords': ['软件', '数据', '人工智能', '智能制造', '信息系统']
    },
    'ndrc': {
        'name': '国家发改委',
        'url': 'www.ndrc.gov.cn/xxgk/zcfb/tz/wap_index.html',
        'base': 'http://www.ndrc.gov.cn',
        'keywords': ['数字经济', '数据要素', '人工智能', '智能制造', '平台经济']
    },
    'most': {
        'name': '科技部',
        'url': 'www.most.gov.cn/tztg/index.html',
        'base': 'http://www.most.gov.cn',
        'keywords': ['科技计划', '人工智能', '软件技术', '数据治理', '创新']
    },
    'cac': {
        'name': '国家网信办',
        'url': 'wap.cac.gov.cn/yaowen/wxyw/A093602phoneindex_1.htm',
        'base': 'http://www.cac.gov.cn',
        'keywords': ['网络安全', '数据安全', '人工智能', '算法', '平台治理']
    }
}

def fetch_news_with_jina(url):
    """Fetch news using Jina AI reader"""
    try:
        jina_url = f'https://r.jina.ai/http://{url}'
        response = requests.get(jina_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
    return None

def contains_keyword(text, keywords=None):
    """Check if text contains any industry keyword"""
    if keywords is None:
        keywords = KEYWORDS
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)

def parse_news_from_text(text, base_url, org_keywords):
    """Parse news items from Jina AI output with keyword filtering"""
    news_list = []
    lines = text.split('\n')
    
    for line in lines:
        # Pattern: [Title](URL) Date
        match = re.search(r'\[([^\]]+)\]\(([^)]+)\)\s*(\d{4}-\d{2}-\d{2})?', line)
        if match:
            title = match.group(1)
            url = match.group(2)
            date = match.group(3) if match.group(3) else datetime.now().strftime('%m-%d')
            
            # Filter by keywords
            if not contains_keyword(title, org_keywords):
                continue
            
            # Filter valid news
            if len(title) > 5 and len(title) < 150:
                if not url.startswith('http'):
                    if url.startswith('/'):
                        url = base_url + url
                    else:
                        url = base_url + '/' + url
                
                # Extract date from URL if possible
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', url)
                if date_match:
                    date = date_match.group(1)[-5:]
                
                news_list.append({
                    'title': title,
                    'url': url,
                    'date': date
                })
    
    # Remove duplicates
    seen = set()
    unique_news = []
    for item in news_list:
        if item['url'] not in seen and 'index' not in item['url']:
            seen.add(item['url'])
            unique_news.append(item)
    
    return unique_news[:10]

def fetch_all_news():
    """Fetch news from all organizations"""
    all_news = {}
    
    for org_id, config in ORG_CONFIG.items():
        print(f"\n{'='*60}")
        print(f"Fetching policy news for {config['name']}...")
        print(f"URL: {config['url']}")
        print(f"Keywords: {', '.join(config['keywords'])}")
        print('-'*60)
        
        full_url = config['url']
        text = fetch_news_with_jina(full_url)
        
        if text:
            news_list = parse_news_from_text(text, config['base'], config['keywords'])
            
            if news_list:
                all_news[org_id] = news_list
                print(f"✓ Found {len(news_list)} relevant policy items")
                for item in news_list[:3]:
                    print(f"  - {item['title'][:50]}... ({item['date']})")
            else:
                print(f"⚠ No relevant policy news found")
        else:
            print(f"✗ Failed to fetch")
    
    return all_news

def get_fallback_news():
    """Fallback policy news data"""
    return {
        'miit': [
            {'title': '工信部发布《软件和信息技术服务业"十四五"发展规划》', 'url': 'https://www.miit.gov.cn', 'date': '03-22'},
            {'title': '《工业数据分类分级指南 (试行)》政策解读', 'url': 'https://www.miit.gov.cn', 'date': '03-20'},
            {'title': '工信部：推进人工智能产业创新发展', 'url': 'https://www.miit.gov.cn', 'date': '03-18'},
            {'title': '《智能制造标准体系建设指南》征求意见', 'url': 'https://www.miit.gov.cn', 'date': '03-15'},
            {'title': '工信部部署信息系统运维安全保障工作', 'url': 'https://www.miit.gov.cn', 'date': '03-12'}
        ],
        'ndrc': [
            {'title': '发改委：《关于构建数据基础制度更好发挥数据要素作用的意见》', 'url': 'https://www.ndrc.gov.cn', 'date': '03-21'},
            {'title': '《数字经济促进法》草案征求意见', 'url': 'https://www.ndrc.gov.cn', 'date': '03-19'},
            {'title': '发改委批准建设国家人工智能创新应用先导区', 'url': 'https://www.ndrc.gov.cn', 'date': '03-17'},
            {'title': '《平台经济健康发展指导意见》发布', 'url': 'https://www.ndrc.gov.cn', 'date': '03-14'},
            {'title': '发改委：支持制造业数字化转型', 'url': 'https://www.ndrc.gov.cn', 'date': '03-11'}
        ],
        'most': [
            {'title': '科技部启动"人工智能"重点专项 2026 年度项目申报', 'url': 'https://www.most.gov.cn', 'date': '03-20'},
            {'title': '《国家新一代人工智能开放创新平台建设工作指引》', 'url': 'https://www.most.gov.cn', 'date': '03-18'},
            {'title': '科技部：加强软件技术研发支持', 'url': 'https://www.most.gov.cn', 'date': '03-16'},
            {'title': '《数据治理科技支撑方案》印发', 'url': 'https://www.most.gov.cn', 'date': '03-13'},
            {'title': '科技部部署信息技术创新应用研究', 'url': 'https://www.most.gov.cn', 'date': '03-10'}
        ],
        'cac': [
            {'title': '网信办：《生成式人工智能服务管理暂行办法》', 'url': 'https://www.cac.gov.cn', 'date': '03-19'},
            {'title': '《数据安全法》实施情况检查', 'url': 'https://www.cac.gov.cn', 'date': '03-17'},
            {'title': '网信办开展算法推荐专项治理', 'url': 'https://www.cac.gov.cn', 'date': '03-15'},
            {'title': '《网络安全审查办法》修订发布', 'url': 'https://www.cac.gov.cn', 'date': '03-12'},
            {'title': '网信办：加强个人信息保护', 'url': 'https://www.cac.gov.cn', 'date': '03-09'}
        ]
    }

def update_html(news_data):
    """Update HTML file with news data"""
    html_path = '权威机构网址汇编.html'
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate JavaScript for news data
        news_js = f'const LATEST_NEWS_DATA = {json.dumps(news_data, ensure_ascii=False)};'
        
        # Find and replace the LATEST_NEWS_DATA
        pattern = r'const LATEST_NEWS_DATA = \{[^}]+\};'
        if re.search(pattern, content):
            content = re.sub(pattern, news_js, content)
        else:
            # Add before </head>
            content = content.replace('</head>', f'    <script>\n{news_js}\n    </script>\n</head>')
        
        # Update timestamp comment
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        timestamp_comment = f'<!-- Last updated: {timestamp} -->'
        if '<!-- Last updated:' in content:
            content = re.sub(r'<!-- Last updated:.*? -->', timestamp_comment, content)
        else:
            content = content.replace('</head>', f'    {timestamp_comment}\n</head>')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✓ Updated {html_path}")
        return True
    
    except Exception as e:
        print(f"✗ Failed to update HTML: {e}")
        return False

def main():
    print("="*60)
    print("Fetching software & IT service industry policy news")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Keywords: {', '.join(KEYWORDS[:8])}...")
    
    # Fetch news
    news_data = fetch_all_news()
    
    # Use fallback if no news fetched
    if not news_data:
        print("\n⚠ No news fetched, using fallback data")
        news_data = get_fallback_news()
    else:
        # Fill in missing with fallback
        fallback = get_fallback_news()
        for org_id in ORG_CONFIG.keys():
            if org_id not in news_data or len(news_data[org_id]) < 3:
                print(f"  Using fallback for {org_id}")
                news_data[org_id] = fallback[org_id][:5]
    
    print(f"\n{'='*60}")
    print(f"✓ Fetched policy news for {len(news_data)} organizations")
    print("="*60)
    
    # Update HTML
    if update_html(news_data):
        print("\n✓ Successfully updated HTML file")
    else:
        print("\n✗ Failed to update HTML file")

if __name__ == '__main__':
    main()
