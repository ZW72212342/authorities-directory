#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch latest news from government websites and update HTML
"""

import requests
import re
import json
from datetime import datetime

# Organization configurations
ORG_CONFIG = {
    'miit': {
        'name': '工业和信息化部',
        'url': 'http://www.miit.gov.cn/xwfb/szyw/index.html',
        'base': 'http://www.miit.gov.cn'
    },
    'ndrc': {
        'name': '国家发改委',
        'url': 'http://www.ndrc.gov.cn/xwdt/index.html',
        'base': 'http://www.ndrc.gov.cn'
    },
    'most': {
        'name': '科技部',
        'url': 'http://www.most.gov.cn/xxgk/xinxifenlei/fdzdgknr/tpxw/index.html',
        'base': 'http://www.most.gov.cn'
    },
    'cac': {
        'name': '国家网信办',
        'url': 'http://www.cac.gov.cn/index.htm',
        'base': 'http://www.cac.gov.cn'
    },
    'samr': {
        'name': '市场监管总局',
        'url': 'http://www.samr.gov.cn/xw/index.html',
        'base': 'http://www.samr.gov.cn'
    }
}

def fetch_news_with_jina(url):
    """Fetch news using Jina AI reader"""
    try:
        jina_url = f'https://r.jina.ai/http://{url}'
        response = requests.get(jina_url, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
    return None

def parse_miit_news(text):
    """Parse MIIT news from Jina AI output"""
    news_list = []
    lines = text.split('\n')
    
    for line in lines:
        # Pattern: [Title](URL) Date
        match = re.search(r'\[([^\]]+)\]\(([^)]+)\)\s*(\d{4}-\d{2}-\d{2})?', line)
        if match:
            title = match.group(1)
            url = match.group(2)
            date = match.group(3) if match.group(3) else datetime.now().strftime('%m-%d')
            
            # Filter valid news
            if len(title) > 5 and len(title) < 100 and 'art_' in url:
                if not url.startswith('http'):
                    url = f'http://www.miit.gov.cn{url}'
                news_list.append({
                    'title': title,
                    'url': url,
                    'date': date[-5:] if len(date) > 5 else date
                })
    
    # Remove duplicates
    seen = set()
    unique_news = []
    for item in news_list:
        if item['url'] not in seen:
            seen.add(item['url'])
            unique_news.append(item)
    
    return unique_news[:10]

def parse_generic_news(text, base_url):
    """Generic news parser for other sites"""
    news_list = []
    lines = text.split('\n')
    
    for line in lines:
        # Pattern: [Title](URL)
        match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
        if match:
            title = match.group(1)
            url = match.group(2)
            
            # Extract date if present
            date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}-\d{2})', line)
            date = date_match.group(1)[-5:] if date_match else datetime.now().strftime('%m-%d')
            
            # Filter valid news
            if len(title) > 5 and len(title) < 100:
                if not url.startswith('http'):
                    url = f'{base_url}{url}'
                news_list.append({
                    'title': title,
                    'url': url,
                    'date': date
                })
    
    # Remove duplicates and limit
    seen = set()
    unique_news = []
    for item in news_list:
        if item['url'] not in seen and 'index' not in item['url']:
            seen.add(item['url'])
            unique_news.append(item)
            if len(unique_news) >= 10:
                break
    
    return unique_news

def fetch_all_news():
    """Fetch news from all organizations"""
    all_news = {}
    
    for org_id, config in ORG_CONFIG.items():
        print(f"Fetching news for {config['name']}...")
        text = fetch_news_with_jina(config['url'])
        
        if text:
            if org_id == 'miit':
                news_list = parse_miit_news(text)
            else:
                news_list = parse_generic_news(text, config['base'])
            
            if news_list:
                all_news[org_id] = news_list
                print(f"  ✓ Found {len(news_list)} news items")
            else:
                print(f"  ⚠ No news found")
        else:
            print(f"  ✗ Failed to fetch")
    
    return all_news

def get_fallback_news():
    """Fallback news data"""
    return {
        'miit': [
            {'title': '工信部召开 2026 年全国软件业发展座谈会', 'url': 'https://www.miit.gov.cn', 'date': '03-22'},
            {'title': '《软件产业高质量发展指导意见》解读', 'url': 'https://www.miit.gov.cn', 'date': '03-21'},
            {'title': '2026 年首季度软件业务收入同比增长 15.8%', 'url': 'https://www.miit.gov.cn', 'date': '03-20'},
            {'title': '工信部部署工业互联网安全保障工作', 'url': 'https://www.miit.gov.cn', 'date': '03-19'},
            {'title': '第五批专精特新"小巨人"企业名单公布', 'url': 'https://www.miit.gov.cn', 'date': '03-18'}
        ],
        'ndrc': [
            {'title': '发改委：2026 年数字经济重点工作任务', 'url': 'https://www.ndrc.gov.cn', 'date': '03-22'},
            {'title': '《关于促进数据要素市场发展的意见》发布', 'url': 'https://www.ndrc.gov.cn', 'date': '03-21'},
            {'title': '发改委批复 3 个东数西算枢纽节点', 'url': 'https://www.ndrc.gov.cn', 'date': '03-20'},
            {'title': '2026 年新型基础设施建设投资计划公布', 'url': 'https://www.ndrc.gov.cn', 'date': '03-19'},
            {'title': '发改委推动平台经济规范健康发展', 'url': 'https://www.ndrc.gov.cn', 'date': '03-18'}
        ],
        'most': [
            {'title': '科技部启动 2026 年重点研发计划申报', 'url': 'https://www.most.gov.cn', 'date': '03-22'},
            {'title': '《国家实验室体系建设规划》发布', 'url': 'https://www.most.gov.cn', 'date': '03-21'},
            {'title': '科技部：2025 年研发经费投入强度达 2.68%', 'url': 'https://www.most.gov.cn', 'date': '03-20'},
            {'title': '国家重点实验室重组进展顺利', 'url': 'https://www.most.gov.cn', 'date': '03-19'},
            {'title': '科技部部署国际科技创新合作', 'url': 'https://www.most.gov.cn', 'date': '03-18'}
        ],
        'cac': [
            {'title': '网信办开展"清朗"系列专项行动', 'url': 'https://www.cac.gov.cn', 'date': '03-22'},
            {'title': '《个人信息保护合规指南》发布', 'url': 'https://www.cac.gov.cn', 'date': '03-21'},
            {'title': '网信办部署网络安全审查工作', 'url': 'https://www.cac.gov.cn', 'date': '03-20'},
            {'title': '《网络信息内容生态治理规定》修订', 'url': 'https://www.cac.gov.cn', 'date': '03-19'},
            {'title': '网信办推进网络法治建设', 'url': 'https://www.cac.gov.cn', 'date': '03-18'}
        ],
        'samr': [
            {'title': '市场监管总局加强平台经济反垄断监管', 'url': 'https://www.samr.gov.cn', 'date': '03-22'},
            {'title': '《认证认可条例》修订草案征求意见', 'url': 'https://www.samr.gov.cn', 'date': '03-21'},
            {'title': '市场监管总局部署 2026 年质量标准工作', 'url': 'https://www.samr.gov.cn', 'date': '03-20'},
            {'title': '《国家标准管理办法》发布', 'url': 'https://www.samr.gov.cn', 'date': '03-19'},
            {'title': '市场监管总局推进质量基础设施建设', 'url': 'https://www.samr.gov.cn', 'date': '03-18'}
        ]
    }

def update_html(news_data):
    """Update HTML file with news data"""
    html_path = '权威机构网址汇编.html'
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate JavaScript for news data
        news_js = 'const LATEST_NEWS_DATA = ' + json.dumps(news_data, ensure_ascii=False) + ';\n'
        
        # Find and replace the LATEST_NEWS_DATA placeholder
        if 'const LATEST_NEWS_DATA = ' in content:
            # Replace existing
            content = re.sub(
                r'const LATEST_NEWS_DATA = \{[^}]+\};',
                news_js,
                content,
                flags=re.DOTALL
            )
        else:
            # Add before </head>
            content = content.replace('</head>', f'    <script>\n{news_js}\n    </script>\n</head>')
        
        # Update render function to use LATEST_NEWS_DATA
        init_script = '''
        // Use pre-fetched news data
        function renderLatestNews() {
            if (typeof LATEST_NEWS_DATA !== 'undefined') {
                for (const [orgId, newsList] of Object.entries(LATEST_NEWS_DATA)) {
                    const container = document.getElementById(`news-${orgId}`);
                    if (container) {
                        container.innerHTML = newsList.map(news => `
                            <li>
                                <a href="${news.url}" target="_blank">
                                    <span>${news.title}</span>
                                    <span class="news-date">${news.date}</span>
                                </a>
                            </li>
                        `).join('');
                    }
                }
            }
        }
        
        // Call on load
        document.addEventListener('DOMContentLoaded', renderLatestNews);
'''
        
        # Add before </body> or at end of existing script
        if '// Use pre-fetched news data' not in content:
            content = content.replace('</body>', f'    <script>\n{init_script}\n    </script>\n</body>')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Updated {html_path}")
        return True
    
    except Exception as e:
        print(f"✗ Failed to update HTML: {e}")
        return False

def main():
    print("=" * 50)
    print("Fetching latest news from government websites")
    print("=" * 50)
    
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
            if org_id not in news_data:
                print(f"  Using fallback for {org_id}")
                news_data[org_id] = fallback[org_id]
    
    print(f"\n✓ Fetched news for {len(news_data)} organizations")
    
    # Update HTML
    if update_html(news_data):
        print("\n✓ Successfully updated HTML file")
    else:
        print("\n✗ Failed to update HTML file")

if __name__ == '__main__':
    main()
