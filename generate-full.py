#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate complete methodology-full.html from CSV
"""

import csv

# Read the CSV data
dimensions = {}
with open('游戏评判维度表.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if len(row) >= 4:
            primary = row[0].strip()
            secondary = row[1].strip()
            definition = row[2].strip()
            criteria = row[3].strip()
            if primary not in dimensions:
                dimensions[primary] = []
            dimensions[primary].append((secondary, definition, criteria))

# Score descriptions
score_descriptions = {
    0: '完全没有/缺失',
    1: '极差/行业下游',
    2: '较差/低于平均',
    3: '合格/行业平均',
    4: '优秀/行业上游',
    5: '顶尖/业内标杆'
}

# Section icons
section_icons = {
    '挑战': '⚔️',
    '操作': '🎮',
    '策略': '🧠',
    '成长': '📈',
    '画音': '🎨',
    '幻想': '🌌',
    '竞争': '🏆',
    '剧情': '📖',
    '破坏': '💥',
    '情感': '❤️',
    '人设': '👤',
    '设计': '⚙️',
    '收集': '🎁',
    '探索': '🗺️',
    '团队': '👥',
    '休闲': '☕',
    '题材': '🎭',
    'IP': '©️',
    '商业化': '💰',
    '技术': '🔧',
}

section_ids = {
    '挑战': 'challenge',
    '操作': 'control',
    '策略': 'strategy',
    '成长': 'growth',
    '画音': 'audiovisual',
    '幻想': 'fantasy',
    '竞争': 'competition',
    '剧情': 'story',
    '破坏': 'destruction',
    '情感': 'emotion',
    '人设': 'character',
    '设计': 'design',
    '收集': 'collection',
    '探索': 'exploration',
    '团队': 'team',
    '休闲': 'casual',
    '题材': 'theme',
    'IP': 'ip',
    '商业化': 'monetization',
    '技术': 'technology',
}

# HTML template start
html_start = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏设计方法论 - 完整维度版 | Terry Game Lab</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary-gradient: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            --secondary-gradient: linear-gradient(135deg, #00f5d4 0%, #00bbf9 100%);
            --card-bg: rgba(15, 12, 41, 0.85);
            --card-border: rgba(0, 245, 212, 0.2);
            --text-primary: #ffffff;
            --text-secondary: rgba(255, 255, 255, 0.92);
            --text-muted: rgba(255, 255, 255, 0.7);
            --accent-gold: #00f5d4;
            --accent-cyan: #f15bb5;
            --score-0: #ff4757;
            --score-1: #ff6b6b;
            --score-2: #ffd166;
            --score-3: #06d6a0;
            --score-4: #118ab2;
            --score-5: #073b4c;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--primary-gradient);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.75;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
            letter-spacing: 0.01em;
            position: relative;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                url('https://images.unsplash.com/photo-1550745165-9bc0b252726f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80') 
                center/cover no-repeat;
            opacity: 0.08;
            z-index: -1;
            mix-blend-mode: screen;
            background-attachment: fixed;
        }
        
        /* Header */
        .header {
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid var(--card-border);
        }
        
        .nav-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            letter-spacing: -0.02em;
        }
        
        .logo:hover {
            opacity: 0.9;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
            list-style: none;
            font-weight: 500;
        }
        
        .nav-links a {
            color: var(--text-secondary);
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .nav-links a:hover,
        .nav-links a.active {
            color: var(--accent-gold);
        }
        
        /* Hero Section */
        .hero {
            text-align: center;
            padding: 5rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .hero h1 {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            text-shadow: 0 0 20px rgba(0, 245, 212, 0.5), 0 0 40px rgba(0, 245, 212, 0.3);
            letter-spacing: -0.03em;
            background: linear-gradient(45deg, #00f5d4, #f15bb5, #00bbf9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: titleGlow 3s ease-in-out infinite alternate;
        }
        
        @keyframes titleGlow {
            0% { filter: brightness(1); }
            100% { filter: brightness(1.3); }
        }
        
        .hero p {
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 800px;
            margin: 0 auto;
            font-weight: 400;
        }
        
        .version-badge {
            display: inline-block;
            background: rgba(0, 245, 212, 0.2);
            color: var(--accent-gold);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-top: 1rem;
            border: 1px solid rgba(0, 245, 212, 0.3);
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        
        /* Quick Nav */
        .quick-nav {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto 4rem;
            border: 1px solid var(--card-border);
        }
        
        .quick-nav h3 {
            font-size: 1.4rem;
            margin-bottom: 1.5rem;
            color: var(--accent-gold);
            font-weight: 700;
        }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        
        .nav-tag {
            background: rgba(255, 255, 255, 0.1);
            padding: 0.8rem 1.2rem;
            border-radius: 12px;
            text-align: center;
            text-decoration: none;
            color: var(--text-primary);
            font-weight: 500;
            transition: all 0.3s ease;
            border: 1px solid transparent;
            font-size: 0.95rem;
        }
        
        .nav-tag:hover {
            background: rgba(0, 245, 212, 0.2);
            border-color: var(--accent-gold);
            transform: translateY(-2px);
        }
        
        /* Scoring Guide */
        .scoring-guide {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto 4rem;
            border: 1px solid var(--card-border);
        }
        
        .scoring-guide h3 {
            font-size: 1.4rem;
            margin-bottom: 1.5rem;
            color: var(--accent-gold);
            font-weight: 700;
        }
        
        .score-levels {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .score-level-item {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding: 0.8rem;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            transition: background 0.2s ease;
        }
        
        .score-level-item:hover {
            background: rgba(255, 255, 255, 0.08);
        }
        
        .score-dot {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        .score-dot.score-0 { background: var(--score-0); }
        .score-dot.score-1 { background: var(--score-1); }
        .score-dot.score-2 { background: var(--score-2); }
        .score-dot.score-3 { background: var(--score-3); }
        .score-dot.score-4 { background: var(--score-4); }
        .score-dot.score-5 { background: var(--score-5); }
        
        .score-label {
            font-weight: 600;
            min-width: 60px;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .score-desc {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        /* Main Content */
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 0 2rem 5rem;
        }
        
        .dimension-section {
            margin-bottom: 5rem;
            scroll-margin-top: 120px;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 1.2rem;
            margin-bottom: 2.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--card-border);
        }
        
        .section-icon {
            font-size: 2.5rem;
            width: 70px;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--secondary-gradient);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 187, 249, 0.3);
        }
        
        .section-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }
        
        /* Section Numbering */
        .section-title::before {
            content: attr(data-section-number);
            display: inline-block;
            width: 45px;
            height: 45px;
            line-height: 45px;
            text-align: center;
            background: linear-gradient(135deg, #f15bb5 0%, #00f5d4 100%);
            color: #0f0c29;
            border-radius: 12px;
            font-size: 1.2rem;
            font-weight: 800;
            margin-right: 1rem;
            box-shadow: 0 4px 15px rgba(241, 91, 181, 0.4);
            font-family: 'JetBrains Mono', monospace;
        }
        
        /* Back to Top Button */
        .back-to-top {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #00f5d4 0%, #00bbf9 100%);
            border: 2px solid #00f5d4;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: #0f0c29;
            cursor: pointer;
            z-index: 10000;
            box-shadow: 0 0 20px rgba(0, 245, 212, 0.5),
                        inset 0 0 10px rgba(0, 245, 212, 0.3);
            transition: all 0.3s ease;
            opacity: 0;
            visibility: hidden;
            animation: buttonGlow 2s ease-in-out infinite alternate;
        }
        
        .back-to-top.show {
            opacity: 1;
            visibility: visible;
        }
        
        .back-to-top:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(0, 245, 212, 0.7),
                        inset 0 0 15px rgba(0, 245, 212, 0.4);
        }
        
        @keyframes buttonGlow {
            0% { filter: brightness(1); }
            100% { filter: brightness(1.3); }
        }
        
        .items-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2.5rem;
        }
        
        @media (max-width: 1024px) {
            .items-grid {
                grid-template-columns: 1fr;
                gap: 2rem;
            }
        }
        
        .dimension-card {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid var(--card-border);
            transition: all 0.3s ease;
        }
        
        .dimension-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            border-color: rgba(241, 91, 181, 0.3);
        }
        
        .dimension-title {
            font-size: 1.35rem;
            font-weight: 600;
            color: var(--accent-cyan);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            letter-spacing: -0.01em;
            text-shadow: 0 0 10px rgba(241, 91, 181, 0.4);
        }
        
        .dimension-definition {
            color: var(--text-secondary);
            margin-bottom: 1.5rem;
            font-size: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--card-border);
            font-style: italic;
            font-weight: 400;
        }
        
        .score-section {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
        }
        
        .score-section .score-label {
            font-weight: 600;
            color: var(--accent-gold);
            margin-bottom: 1rem;
            font-size: 1.1rem;
            font-family: inherit;
            min-width: auto;
        }
        
        .score-criteria {
            margin-bottom: 1rem;
            color: var(--text-secondary);
            font-size: 0.95rem;
            padding: 0.75rem;
            background: rgba(0, 245, 212, 0.1);
            border-radius: 10px;
            border-left: 3px solid var(--accent-gold);
            font-weight: 400;
        }
        
        .score-grid {
            display: grid;
            gap: 0.8rem;
        }
        
        .score-item {
            display: flex;
            gap: 0.8rem;
            align-items: center;
            padding: 0.75rem 1rem;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.05);
            transition: background 0.2s ease;
            flex-wrap: nowrap;
        }
        
        .score-value {
            min-width: 30px;
            font-weight: 700;
            font-size: 1.1rem;
            font-family: 'JetBrains Mono', monospace;
            flex-shrink: 0;
        }
        
        .score-text {
            color: var(--text-secondary);
            font-size: 0.95rem;
            flex: 1;
            line-height: 1.6;
        }
        
        /* Footer */
        footer {
            background: rgba(0, 0, 0, 0.4);
            padding: 2rem;
            text-align: center;
            border-top: 1px solid var(--card-border);
        }
        
        footer p {
            color: var(--text-muted);
            font-size: 0.95rem;
            font-weight: 400;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .nav-container {
                padding: 1rem;
            }
            
            .logo {
                font-size: 1.4rem;
            }
            
            .nav-links {
                display: none;
            }
            
            .hero {
                padding: 3rem 1rem;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .hero p {
                font-size: 1rem;
            }
            
            .quick-nav {
                margin: 0 1rem 3rem;
                padding: 1.5rem;
            }
            
            .nav-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .scoring-guide {
                margin: 0 1rem 3rem;
                padding: 1.5rem;
            }
            
            .score-levels {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 0 1rem 3rem;
            }
            
            .section-title {
                font-size: 1.6rem;
            }
            
            .items-grid {
                grid-template-columns: 1fr;
            }
            
            .dimension-card {
                padding: 1.5rem;
            }
            
            .back-to-top {
                width: 50px;
                height: 50px;
                font-size: 1.5rem;
                bottom: 20px;
                right: 20px;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="nav-container">
            <a href="index.html" class="logo">
                🎮 Terry Game Lab
            </a>
            <ul class="nav-links">
                <li><a href="index.html">首页</a></li>
                <li><a href="methodology.html">精简版方法论</a></li>
                <li><a href="methodology-full.html" class="active">完整版维度表</a></li>
                <li><a href="#">游戏评测</a></li>
            </ul>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <h1>🎮 游戏设计方法论 - 完整版</h1>
        <p>基于67个专业评估维度的科学游戏评判体系，覆盖从核心玩法到商业化的全流程设计标准</p>
        <span class="version-badge">📊 维度版本：2026.03 | 评估粒度：0-5分制</span>
    </section>

    <!-- Scoring Guide -->
    <section class="scoring-guide">
        <h3>📋 评分标准说明</h3>
        <div class="score-levels">
'''

for score in range(0, 6):
    html_start += f'''            <div class="score-level-item">
                <span class="score-dot score-{score}"></span>
                <span class="score-label">{score}分</span>
                <span class="score-desc">{score_descriptions[score]}</span>
            </div>
'''

html_start += '''        </div>
    </section>

    <!-- Quick Navigation -->
    <section class="quick-nav">
        <h3>⚡ 快速导航</h3>
        <div class="nav-grid">
'''

# Add quick nav
for primary in dimensions.keys():
    icon = section_icons.get(primary, '📌')
    section_id = section_ids.get(primary, primary.lower())
    html_start += f'            <a href="#{section_id}" class="nav-tag">{icon} {primary}</a>\n'

html_start += '''        </div>
    </section>

    <!-- Main Content -->
    <main class="container">
'''

# Add sections
section_number = 1
for primary, secondary_list in dimensions.items():
    icon = section_icons.get(primary, '📌')
    section_id = section_ids.get(primary, primary.lower())
    section_num_str = f'{section_number:02d}'
    html_start += f'''        <!-- {primary}维度 -->
        <section id="{section_id}" class="dimension-section">
            <div class="section-header">
                <div class="section-icon">{icon}</div>
                <h2 class="section-title" data-section-number="{section_num_str}">{primary}</h2>
            </div>
            
            <div class="items-grid">
'''
    
    for (secondary, definition, criteria) in secondary_list:
        html_start += f'''                <div class="dimension-card">
                    <h3 class="dimension-title">{secondary}</h3>
                    <p class="dimension-definition">{definition}</p>
                    <div class="score-section">
                        <div class="score-label">评估维度</div>
                        <div class="score-criteria">{criteria}</div>
                        <div class="score-grid">
'''
        
        for score in range(0, 6):
            score_color = f'var(--score-{score})'
            if score == 0:
                desc = '完全没有'
            elif score == 1:
                desc = '极差，行业下游水平'
            elif score == 2:
                desc = '较差，低于行业平均'
            elif score == 3:
                desc = '合格，达到行业平均'
            elif score == 4:
                desc = '优秀，达到行业上游水平'
            else:
                desc = '顶尖，业内标杆水平'
            # Get description based on score
            if score == 0:
                text = f'完全没有{secondary}'
            elif score == 1:
                text = f'{secondary}极差，几乎没有，行业下游'
            elif score == 2:
                text = f'{secondary}较差，低于行业平均水平'
            elif score == 3:
                text = f'{secondary}合格，达到行业平均水平'
            elif score == 4:
                text = f'{secondary}优秀，达到行业上游水平'
            else:
                text = f'{secondary}顶尖，业内标杆水平'
            
            html_start += f'''                            <div class="score-item">
                                <span class="score-value" style="color: {score_color}">{score}</span>
                                <span class="score-text">{text}</span>
                            </div>
'''
        
        html_start += '''                        </div>
                    </div>
                </div>
'''
    
    html_start += '''            </div>
        </section>
'''
    section_number += 1

# HTML end
html_end = '''    </main>

    <!-- Back to Top Button -->
    <div class="back-to-top" id="backToTop" onclick="scrollToTop()">
        ↑
    </div>

    <!-- Footer -->
    <footer>
        <p>© 2024 Terry Game Lab. Powered by passion for games.</p>
    </footer>

    <script>
        // Back to Top functionality
        const backToTopButton = document.getElementById('backToTop');
        
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
    </script>
</body>
</html>'''

# Combine all
full_html = html_start + html_end

# Write to file
with open('methodology-full.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"Generated methodology-full.html with {sum(len(v) for v in dimensions.values())} dimensions")
